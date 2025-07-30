// #[cfg(test)]
pub mod test;

pub mod rank_0;
pub mod rank_1;
pub mod rank_2;
pub mod rank_3;
pub mod rank_4;

use super::{SquareMatrix, Vector};
use crate::defeat_message;
use rank_0::TensorRank0;
use std::{
    fmt::{self, Debug, Display, Formatter},
    ops::{Add, AddAssign, Div, DivAssign, Index, IndexMut, Mul, MulAssign, Sub, SubAssign},
};

/// A scalar.
pub type Scalar = TensorRank0;

/// Possible errors for tensors.
#[derive(PartialEq)]
pub enum TensorError {
    NotPositiveDefinite,
}

impl Debug for TensorError {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        let error = match self {
            Self::NotPositiveDefinite => "\x1b[1;91mResult is not positive definite.".to_string(),
        };
        write!(f, "\n{error}\n\x1b[0;2;31m{}\x1b[0m\n", defeat_message())
    }
}

impl Display for TensorError {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        let error = match self {
            Self::NotPositiveDefinite => "\x1b[1;91mResult is not positive definite.".to_string(),
        };
        write!(f, "{error}\x1b[0m")
    }
}

/// Common methods for solutions.
pub trait Solution
where
    Self: Tensor,
{
    /// Decrements the solution chained with a vector from another vector.
    fn decrement_from_chained(&mut self, other: &mut Vector, vector: Vector);
}

/// Common methods for Jacobians.
pub trait Jacobian
where
    Self: Tensor + Sub<Vector, Output = Self> + for<'a> Sub<&'a Vector, Output = Self>,
{
    /// Fills the Jacobian into a vector.
    fn fill_into(self, vector: &mut Vector);
    /// Fills the Jacobian chained with a vector into another vector.
    fn fill_into_chained(self, other: Vector, vector: &mut Vector);
}

/// Common methods for Hessians.
pub trait Hessian
where
    Self: Tensor,
{
    /// Fills the Hessian into a square matrix.
    fn fill_into(self, square_matrix: &mut SquareMatrix);
}

/// Common methods for rank-2 tensors.
pub trait Rank2
where
    Self: Sized,
{
    /// The type that is the transpose of the tensor.
    type Transpose;
    /// Returns the deviatoric component of the rank-2 tensor.
    fn deviatoric(&self) -> Self;
    /// Returns the deviatoric component and trace of the rank-2 tensor.
    fn deviatoric_and_trace(&self) -> (Self, TensorRank0);
    /// Checks whether the tensor is a diagonal tensor.
    fn is_diagonal(&self) -> bool;
    /// Checks whether the tensor is the identity tensor.
    fn is_identity(&self) -> bool;
    /// Returns the second invariant of the rank-2 tensor.
    fn second_invariant(&self) -> TensorRank0 {
        0.5 * (self.trace().powi(2) - self.squared_trace())
    }
    /// Returns the trace of the rank-2 tensor squared.
    fn squared_trace(&self) -> TensorRank0;
    /// Returns the trace of the rank-2 tensor.
    fn trace(&self) -> TensorRank0;
    /// Returns the transpose of the rank-2 tensor.
    fn transpose(&self) -> Self::Transpose;
}

/// Common methods for tensors.
pub trait Tensor
where
    for<'a> Self: Sized
        + Debug
        + Display
        + Add<Self, Output = Self>
        + Add<&'a Self, Output = Self>
        + AddAssign
        + AddAssign<&'a Self>
        + Clone
        + Div<TensorRank0, Output = Self>
        + DivAssign<TensorRank0>
        + Mul<TensorRank0, Output = Self>
        + MulAssign<TensorRank0>
        + Sub<Self, Output = Self>
        + Sub<&'a Self, Output = Self>
        + SubAssign
        + SubAssign<&'a Self>,
    Self::Item: Tensor,
{
    /// The type of item encountered when iterating over the tensor.
    type Item;
    /// Returns the full contraction with another tensor.
    fn full_contraction(&self, tensor: &Self) -> TensorRank0 {
        self.iter()
            .zip(tensor.iter())
            .map(|(self_entry, tensor_entry)| self_entry.full_contraction(tensor_entry))
            .sum()
    }
    /// Checks whether the tensor is the zero tensor.
    fn is_zero(&self) -> bool {
        self.iter().filter(|entry| !entry.is_zero()).count() == 0
    }
    /// Returns an iterator.
    ///
    /// The iterator yields all items from start to end. [Read more](https://doc.rust-lang.org/std/iter/)
    fn iter(&self) -> impl Iterator<Item = &Self::Item>;
    /// Returns an iterator that allows modifying each value.
    ///
    /// The iterator yields all items from start to end. [Read more](https://doc.rust-lang.org/std/iter/)
    fn iter_mut(&mut self) -> impl Iterator<Item = &mut Self::Item>;
    /// Returns the tensor norm.
    fn norm(&self) -> TensorRank0 {
        self.norm_squared().sqrt()
    }
    /// Returns the infinity norm.
    fn norm_inf(&self) -> TensorRank0 {
        unimplemented!()
    }
    /// Returns the tensor norm squared.
    fn norm_squared(&self) -> TensorRank0 {
        self.full_contraction(self)
    }
    /// Normalizes the tensor.
    fn normalize(&mut self) {
        *self /= self.norm()
    }
    /// Returns the tensor normalized.
    fn normalized(self) -> Self {
        let norm = self.norm();
        self / norm
    }
    /// Returns the total number of entries.
    fn num_entries(&self) -> usize {
        unimplemented!()
    }
}

/// Common methods for tensors derived from arrays.
pub trait TensorArray {
    /// The type of array corresponding to the tensor.
    type Array;
    /// The type of item encountered when iterating over the tensor.
    type Item;
    /// Returns the tensor as an array.
    fn as_array(&self) -> Self::Array;
    /// Returns the identity tensor.
    fn identity() -> Self;
    /// Returns a tensor given an array.
    fn new(array: Self::Array) -> Self;
    /// Returns the zero tensor.
    fn zero() -> Self;
}

/// Common methods for tensors derived from Vec.
pub trait TensorVec
where
    Self: FromIterator<Self::Item> + Index<usize, Output = Self::Item> + IndexMut<usize>,
{
    /// The type of item encountered when iterating over the tensor.
    type Item;
    /// The type of slice corresponding to the tensor.
    type Slice<'a>;
    /// Moves all the items of other into self, leaving other empty.
    fn append(&mut self, other: &mut Self);
    /// Returns `true` if the vector contains no items.
    fn is_empty(&self) -> bool;
    /// Returns the number of items in the vector, also referred to as its ‘length’.
    fn len(&self) -> usize;
    /// Returns a tensor given a slice.
    fn new(slice: Self::Slice<'_>) -> Self;
    /// Appends an item to the back of the Vec.
    fn push(&mut self, item: Self::Item);
    /// Returns the zero tensor.
    fn zero(len: usize) -> Self;
}
