#[cfg(test)]
mod test;

pub mod list;
pub mod list_2d;
pub mod vec;
pub mod vec_2d;

use std::{
    fmt::{Display, Formatter, Result},
    mem::transmute,
    ops::{Add, AddAssign, Div, DivAssign, Index, IndexMut, Mul, MulAssign, Sub, SubAssign},
};

use super::{
    super::write_tensor_rank_0, Jacobian, Solution, Tensor, TensorArray, Vector,
    rank_0::TensorRank0, rank_2::TensorRank2, test::ErrorTensor,
};

/// A *d*-dimensional tensor of rank 1.
///
/// `D` is the dimension, `I` is the configuration.
#[derive(Clone, Debug, PartialEq)]
pub struct TensorRank1<const D: usize, const I: usize>([TensorRank0; D]);

pub const fn tensor_rank_1<const D: usize, const I: usize>(
    array: [TensorRank0; D],
) -> TensorRank1<D, I> {
    TensorRank1(array)
}

impl<const D: usize, const I: usize> Display for TensorRank1<D, I> {
    fn fmt(&self, f: &mut Formatter) -> Result {
        write!(f, "[")?;
        self.iter()
            .try_for_each(|entry| write_tensor_rank_0(f, entry))?;
        write!(f, "\x1B[2D]")
    }
}

impl<const D: usize, const I: usize> TensorRank1<D, I> {
    /// Returns the cross product with another rank-1 tensor.
    pub fn cross(&self, tensor_rank_1: &Self) -> Self {
        if D == 3 {
            let mut output = zero();
            output[0] = self[1] * tensor_rank_1[2] - self[2] * tensor_rank_1[1];
            output[1] = self[2] * tensor_rank_1[0] - self[0] * tensor_rank_1[2];
            output[2] = self[0] * tensor_rank_1[1] - self[1] * tensor_rank_1[0];
            output
        } else {
            panic!()
        }
    }
}

impl<const D: usize, const I: usize> ErrorTensor for TensorRank1<D, I> {
    fn error(
        &self,
        comparator: &Self,
        tol_abs: &TensorRank0,
        tol_rel: &TensorRank0,
    ) -> Option<usize> {
        let error_count = self
            .iter()
            .zip(comparator.iter())
            .filter(|&(&self_i, &comparator_i)| {
                &(self_i - comparator_i).abs() >= tol_abs
                    && &(self_i / comparator_i - 1.0).abs() >= tol_rel
            })
            .count();
        if error_count > 0 {
            Some(error_count)
        } else {
            None
        }
    }
    fn error_fd(&self, comparator: &Self, epsilon: &TensorRank0) -> Option<(bool, usize)> {
        let error_count = self
            .iter()
            .zip(comparator.iter())
            .filter(|&(&self_i, &comparator_i)| {
                &(self_i / comparator_i - 1.0).abs() >= epsilon
                    && (&self_i.abs() >= epsilon || &comparator_i.abs() >= epsilon)
            })
            .count();
        if error_count > 0 {
            Some((true, error_count))
        } else {
            None
        }
    }
}

impl<const D: usize, const I: usize> Solution for TensorRank1<D, I> {
    fn decrement_from_chained(&mut self, _other: &mut Vector, _vector: Vector) {
        unimplemented!()
    }
}

impl<const D: usize, const I: usize> Jacobian for TensorRank1<D, I> {
    fn fill_into(self, _vector: &mut Vector) {
        unimplemented!()
    }
    fn fill_into_chained(self, _other: Vector, _vector: &mut Vector) {
        unimplemented!()
    }
}

impl<const D: usize, const I: usize> Sub<Vector> for TensorRank1<D, I> {
    type Output = Self;
    fn sub(self, _vector: Vector) -> Self::Output {
        unimplemented!()
    }
}

impl<const D: usize, const I: usize> Sub<&Vector> for TensorRank1<D, I> {
    type Output = Self;
    fn sub(self, _vector: &Vector) -> Self::Output {
        unimplemented!()
    }
}

impl<const D: usize, const I: usize> Tensor for TensorRank1<D, I> {
    type Item = TensorRank0;
    fn full_contraction(&self, tensor_rank_1: &Self) -> TensorRank0 {
        self * tensor_rank_1
    }
    fn iter(&self) -> impl Iterator<Item = &Self::Item> {
        self.0.iter()
    }
    fn iter_mut(&mut self) -> impl Iterator<Item = &mut Self::Item> {
        self.0.iter_mut()
    }
    fn norm_inf(&self) -> TensorRank0 {
        self.iter().fold(0.0, |acc, entry| entry.abs().max(acc))
    }
}

impl<const D: usize, const I: usize> IntoIterator for TensorRank1<D, I> {
    type Item = TensorRank0;
    type IntoIter = std::array::IntoIter<Self::Item, D>;
    fn into_iter(self) -> Self::IntoIter {
        self.0.into_iter()
    }
}

impl<const D: usize, const I: usize> TensorArray for TensorRank1<D, I> {
    type Array = [TensorRank0; D];
    type Item = TensorRank0;
    fn as_array(&self) -> Self::Array {
        self.0
    }
    fn identity() -> Self {
        ones()
    }
    fn new(array: Self::Array) -> Self {
        array.into_iter().collect()
    }
    fn zero() -> Self {
        zero()
    }
}

/// Returns the rank-1 tensor of ones as a constant.
pub const fn ones<const D: usize, const I: usize>() -> TensorRank1<D, I> {
    TensorRank1([1.0; D])
}

/// Returns the rank-1 zero tensor as a constant.
pub const fn zero<const D: usize, const I: usize>() -> TensorRank1<D, I> {
    TensorRank1([0.0; D])
}

impl<const D: usize, const I: usize> From<[TensorRank0; D]> for TensorRank1<D, I> {
    fn from(array: [TensorRank0; D]) -> Self {
        Self(array)
    }
}

impl<const D: usize, const I: usize> From<Vec<TensorRank0>> for TensorRank1<D, I> {
    fn from(vec: Vec<TensorRank0>) -> Self {
        Self(vec.try_into().unwrap())
    }
}

impl<const D: usize, const I: usize> From<TensorRank1<D, I>> for [TensorRank0; D] {
    fn from(tensor_rank_1: TensorRank1<D, I>) -> Self {
        tensor_rank_1.0
    }
}

impl<const D: usize, const I: usize> From<TensorRank1<D, I>> for Vec<TensorRank0> {
    fn from(tensor_rank_1: TensorRank1<D, I>) -> Self {
        tensor_rank_1.0.to_vec()
    }
}

impl From<TensorRank1<3, 0>> for TensorRank1<3, 1> {
    fn from(tensor_rank_1: TensorRank1<3, 0>) -> Self {
        unsafe { transmute::<TensorRank1<3, 0>, TensorRank1<3, 1>>(tensor_rank_1) }
    }
}

impl<const D: usize, const I: usize> FromIterator<TensorRank0> for TensorRank1<D, I> {
    fn from_iter<Ii: IntoIterator<Item = TensorRank0>>(into_iterator: Ii) -> Self {
        let mut tensor_rank_1 = zero();
        tensor_rank_1
            .iter_mut()
            .zip(into_iterator)
            .for_each(|(tensor_rank_1_i, value_i)| *tensor_rank_1_i = value_i);
        tensor_rank_1
    }
}

impl<const D: usize, const I: usize> Index<usize> for TensorRank1<D, I> {
    type Output = TensorRank0;
    fn index(&self, index: usize) -> &Self::Output {
        &self.0[index]
    }
}

impl<const D: usize, const I: usize> IndexMut<usize> for TensorRank1<D, I> {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        &mut self.0[index]
    }
}

impl<const D: usize, const I: usize> std::iter::Sum for TensorRank1<D, I> {
    fn sum<Ii>(iter: Ii) -> Self
    where
        Ii: Iterator<Item = Self>,
    {
        let mut output = zero();
        iter.for_each(|item| output += item);
        output
    }
}

impl<const D: usize, const I: usize> Div<TensorRank0> for TensorRank1<D, I> {
    type Output = Self;
    fn div(mut self, tensor_rank_0: TensorRank0) -> Self::Output {
        self /= tensor_rank_0;
        self
    }
}

impl<const D: usize, const I: usize> Div<TensorRank0> for &TensorRank1<D, I> {
    type Output = TensorRank1<D, I>;
    fn div(self, tensor_rank_0: TensorRank0) -> Self::Output {
        self.iter().map(|self_i| self_i / tensor_rank_0).collect()
    }
}

impl<const D: usize, const I: usize> Div<&TensorRank0> for TensorRank1<D, I> {
    type Output = Self;
    fn div(mut self, tensor_rank_0: &TensorRank0) -> Self::Output {
        self /= tensor_rank_0;
        self
    }
}

impl<const D: usize, const I: usize> Div<&TensorRank0> for &TensorRank1<D, I> {
    type Output = TensorRank1<D, I>;
    fn div(self, tensor_rank_0: &TensorRank0) -> Self::Output {
        self.iter().map(|self_i| self_i / tensor_rank_0).collect()
    }
}

impl<const D: usize, const I: usize> DivAssign<TensorRank0> for TensorRank1<D, I> {
    fn div_assign(&mut self, tensor_rank_0: TensorRank0) {
        self.iter_mut().for_each(|self_i| *self_i /= &tensor_rank_0);
    }
}

impl<const D: usize, const I: usize> DivAssign<&TensorRank0> for TensorRank1<D, I> {
    fn div_assign(&mut self, tensor_rank_0: &TensorRank0) {
        self.iter_mut().for_each(|self_i| *self_i /= tensor_rank_0);
    }
}

impl<const D: usize, const I: usize> Mul<TensorRank0> for TensorRank1<D, I> {
    type Output = Self;
    fn mul(mut self, tensor_rank_0: TensorRank0) -> Self::Output {
        self *= tensor_rank_0;
        self
    }
}

impl<const D: usize, const I: usize> Mul<TensorRank0> for &TensorRank1<D, I> {
    type Output = TensorRank1<D, I>;
    fn mul(self, tensor_rank_0: TensorRank0) -> Self::Output {
        self.iter().map(|self_i| self_i * tensor_rank_0).collect()
    }
}

impl<const D: usize, const I: usize> Mul<&TensorRank0> for TensorRank1<D, I> {
    type Output = Self;
    fn mul(mut self, tensor_rank_0: &TensorRank0) -> Self::Output {
        self *= tensor_rank_0;
        self
    }
}

impl<const D: usize, const I: usize> Mul<&TensorRank0> for &TensorRank1<D, I> {
    type Output = TensorRank1<D, I>;
    fn mul(self, tensor_rank_0: &TensorRank0) -> Self::Output {
        self.iter().map(|self_i| self_i * tensor_rank_0).collect()
    }
}

impl<const D: usize, const I: usize> MulAssign<TensorRank0> for TensorRank1<D, I> {
    fn mul_assign(&mut self, tensor_rank_0: TensorRank0) {
        self.iter_mut().for_each(|self_i| *self_i *= &tensor_rank_0);
    }
}

impl<const D: usize, const I: usize> MulAssign<&TensorRank0> for TensorRank1<D, I> {
    fn mul_assign(&mut self, tensor_rank_0: &TensorRank0) {
        self.iter_mut().for_each(|self_i| *self_i *= tensor_rank_0);
    }
}

impl<const D: usize, const I: usize> Add for TensorRank1<D, I> {
    type Output = Self;
    fn add(mut self, tensor_rank_1: Self) -> Self::Output {
        self += tensor_rank_1;
        self
    }
}

impl<const D: usize, const I: usize> Add<&Self> for TensorRank1<D, I> {
    type Output = Self;
    fn add(mut self, tensor_rank_1: &Self) -> Self::Output {
        self += tensor_rank_1;
        self
    }
}

impl<const D: usize, const I: usize> Add<TensorRank1<D, I>> for &TensorRank1<D, I> {
    type Output = TensorRank1<D, I>;
    fn add(self, mut tensor_rank_1: TensorRank1<D, I>) -> Self::Output {
        tensor_rank_1 += self;
        tensor_rank_1
    }
}

impl<const D: usize, const I: usize> AddAssign for TensorRank1<D, I> {
    fn add_assign(&mut self, tensor_rank_1: Self) {
        self.iter_mut()
            .zip(tensor_rank_1.iter())
            .for_each(|(self_i, tensor_rank_1_i)| *self_i += tensor_rank_1_i);
    }
}

impl<const D: usize, const I: usize> AddAssign<&Self> for TensorRank1<D, I> {
    fn add_assign(&mut self, tensor_rank_1: &Self) {
        self.iter_mut()
            .zip(tensor_rank_1.iter())
            .for_each(|(self_i, tensor_rank_1_i)| *self_i += tensor_rank_1_i);
    }
}

impl<const D: usize, const I: usize> Sub for TensorRank1<D, I> {
    type Output = Self;
    fn sub(mut self, tensor_rank_1: Self) -> Self::Output {
        self -= tensor_rank_1;
        self
    }
}

impl<const D: usize, const I: usize> Sub<&Self> for TensorRank1<D, I> {
    type Output = Self;
    fn sub(mut self, tensor_rank_1: &Self) -> Self::Output {
        self -= tensor_rank_1;
        self
    }
}

impl<const D: usize, const I: usize> Sub<TensorRank1<D, I>> for &TensorRank1<D, I> {
    type Output = TensorRank1<D, I>;
    fn sub(self, mut tensor_rank_1: TensorRank1<D, I>) -> Self::Output {
        tensor_rank_1
            .iter_mut()
            .zip(self.iter())
            .for_each(|(tensor_rank_1_i, self_i)| *tensor_rank_1_i = self_i - *tensor_rank_1_i);
        tensor_rank_1
    }
}

impl<const D: usize, const I: usize> Sub<Self> for &TensorRank1<D, I> {
    type Output = TensorRank1<D, I>;
    fn sub(self, tensor_rank_1: Self) -> Self::Output {
        tensor_rank_1
            .iter()
            .zip(self.iter())
            .map(|(tensor_rank_1_i, self_i)| self_i - *tensor_rank_1_i)
            .collect()
    }
}

impl<const D: usize, const I: usize> SubAssign for TensorRank1<D, I> {
    fn sub_assign(&mut self, tensor_rank_1: Self) {
        self.iter_mut()
            .zip(tensor_rank_1.iter())
            .for_each(|(self_i, tensor_rank_1_i)| *self_i -= tensor_rank_1_i);
    }
}

impl<const D: usize, const I: usize> SubAssign<&Self> for TensorRank1<D, I> {
    fn sub_assign(&mut self, tensor_rank_1: &Self) {
        self.iter_mut()
            .zip(tensor_rank_1.iter())
            .for_each(|(self_i, tensor_rank_1_i)| *self_i -= tensor_rank_1_i);
    }
}

impl<const D: usize, const I: usize> Mul for TensorRank1<D, I> {
    type Output = TensorRank0;
    fn mul(self, tensor_rank_1: Self) -> Self::Output {
        self.iter()
            .zip(tensor_rank_1.iter())
            .map(|(self_i, tensor_rank_1_i)| self_i * tensor_rank_1_i)
            .sum()
    }
}

impl<const D: usize, const I: usize> Mul<&Self> for TensorRank1<D, I> {
    type Output = TensorRank0;
    fn mul(self, tensor_rank_1: &Self) -> Self::Output {
        self.iter()
            .zip(tensor_rank_1.iter())
            .map(|(self_i, tensor_rank_1_i)| self_i * tensor_rank_1_i)
            .sum()
    }
}

impl<const D: usize, const I: usize> Mul<TensorRank1<D, I>> for &TensorRank1<D, I> {
    type Output = TensorRank0;
    fn mul(self, tensor_rank_1: TensorRank1<D, I>) -> Self::Output {
        self.iter()
            .zip(tensor_rank_1.iter())
            .map(|(self_i, tensor_rank_1_i)| self_i * tensor_rank_1_i)
            .sum()
    }
}

impl<const D: usize, const I: usize> Mul for &TensorRank1<D, I> {
    type Output = TensorRank0;
    fn mul(self, tensor_rank_1: Self) -> Self::Output {
        self.iter()
            .zip(tensor_rank_1.iter())
            .map(|(self_i, tensor_rank_1_i)| self_i * tensor_rank_1_i)
            .sum()
    }
}

#[allow(clippy::suspicious_arithmetic_impl)]
impl<const D: usize, const I: usize, const J: usize> Div<TensorRank2<D, I, J>>
    for &TensorRank1<D, I>
{
    type Output = TensorRank1<D, J>;
    fn div(self, tensor_rank_2: TensorRank2<D, I, J>) -> Self::Output {
        tensor_rank_2.inverse() * self
    }
}
