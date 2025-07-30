use crate::math::{TensorRank0, TensorRank1Vec, TensorVec};
use std::ops::{Index, IndexMut};

/// A 2D vector of *d*-dimensional tensors of rank 1.
///
/// `D` is the dimension, `I` is the configuration.
#[derive(Clone, Debug)]
pub struct TensorRank1Vec2D<const D: usize, const I: usize>(Vec<TensorRank1Vec<D, I>>);

impl<const D: usize, const I: usize> FromIterator<TensorRank1Vec<D, I>> for TensorRank1Vec2D<D, I> {
    fn from_iter<Ii: IntoIterator<Item = TensorRank1Vec<D, I>>>(into_iterator: Ii) -> Self {
        Self(Vec::from_iter(into_iterator))
    }
}

impl<const D: usize, const I: usize> Index<usize> for TensorRank1Vec2D<D, I> {
    type Output = TensorRank1Vec<D, I>;
    fn index(&self, index: usize) -> &Self::Output {
        &self.0[index]
    }
}

impl<const D: usize, const I: usize> IndexMut<usize> for TensorRank1Vec2D<D, I> {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        &mut self.0[index]
    }
}

impl<const D: usize, const I: usize> TensorVec for TensorRank1Vec2D<D, I> {
    type Item = TensorRank1Vec<D, I>;
    type Slice<'a> = &'a [&'a [[TensorRank0; D]]];
    fn append(&mut self, other: &mut Self) {
        self.0.append(&mut other.0)
    }
    fn is_empty(&self) -> bool {
        self.0.is_empty()
    }
    fn len(&self) -> usize {
        self.0.len()
    }
    fn new(slice: Self::Slice<'_>) -> Self {
        slice
            .iter()
            .map(|slice_entry| Self::Item::new(*slice_entry))
            .collect()
    }
    fn push(&mut self, item: Self::Item) {
        self.0.push(item)
    }
    fn zero(len: usize) -> Self {
        (0..len).map(|_| Self::Item::zero(0)).collect()
    }
}

// impl<const D: usize, const I: usize> Tensor for TensorRank1Vec2D<D, I> {
//     type Item = TensorRank1Vec<D, I>;
//     fn iter(&self) -> impl Iterator<Item = &Self::Item> {
//         self.0.iter()
//     }
//     fn iter_mut(&mut self) -> impl Iterator<Item = &mut Self::Item> {
//         self.0.iter_mut()
//     }
//     fn num_entries(&self) -> usize {
//         todo!()
//     }
// }

impl<const D: usize, const I: usize> TensorRank1Vec2D<D, I> {
    pub fn iter(&self) -> impl Iterator<Item = &TensorRank1Vec<D, I>> {
        self.0.iter()
    }
    pub fn iter_mut(&mut self) -> impl Iterator<Item = &mut TensorRank1Vec<D, I>> {
        self.0.iter_mut()
    }
}
