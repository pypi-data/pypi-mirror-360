//! Mathematics library.

#[cfg(test)]
pub mod test;

/// Special functions.
pub mod special;

/// Integration and ODEs.
pub mod integrate;

/// Interpolation schemes.
pub mod interpolate;

/// Optimization and root finding.
pub mod optimize;

mod matrix;
mod tensor;

pub use matrix::{
    Matrix,
    square::{Banded, SquareMatrix},
    vector::Vector,
};
pub use tensor::{
    Hessian, Jacobian, Rank2, Scalar, Solution, Tensor, TensorArray, TensorVec,
    rank_0::{
        TensorRank0,
        list::{TensorRank0List, tensor_rank_0_list},
    },
    rank_1::{
        TensorRank1,
        list::{TensorRank1List, tensor_rank_1_list},
        list_2d::{TensorRank1List2D, tensor_rank_1_list_2d},
        tensor_rank_1,
        vec::TensorRank1Vec,
        vec_2d::TensorRank1Vec2D,
        zero as tensor_rank_1_zero,
    },
    rank_2::{
        IDENTITY, IDENTITY_00, IDENTITY_10, TensorRank2, ZERO, ZERO_10,
        list::{TensorRank2List, tensor_rank_2_list},
        list_2d::TensorRank2List2D,
        tensor_rank_2,
        vec::TensorRank2Vec,
        vec_2d::TensorRank2Vec2D,
    },
    rank_3::{
        LEVI_CIVITA, TensorRank3, levi_civita, list::TensorRank3List, list_2d::TensorRank3List2D,
        list_3d::TensorRank3List3D,
    },
    rank_4::{
        ContractAllIndicesWithFirstIndicesOf, ContractFirstSecondIndicesWithSecondIndicesOf,
        ContractFirstThirdFourthIndicesWithFirstIndicesOf,
        ContractSecondFourthIndicesWithFirstIndicesOf, ContractSecondIndexWithFirstIndexOf,
        ContractThirdFourthIndicesWithFirstSecondIndicesOf, IDENTITY_1010, TensorRank4,
        list::TensorRank4List,
    },
    test::{TestError, assert_eq, assert_eq_within, assert_eq_within_tols},
};

use std::fmt;

fn write_tensor_rank_0(f: &mut fmt::Formatter, tensor_rank_0: &TensorRank0) -> fmt::Result {
    let num = if tensor_rank_0.abs() > 1e-1 {
        (tensor_rank_0 * 1e6).round() / 1e6
    } else {
        *tensor_rank_0
    };
    let num_abs = num.abs();
    if num.is_nan() {
        write!(f, "{num:>11}, ")
    } else if num == 0.0 || num_abs == 1.0 {
        let temp_1 = format!("{num:>11.6e}, ").to_string();
        let mut temp_2 = temp_1.split("e");
        let a = temp_2.next().unwrap();
        let b = temp_2.next().unwrap();
        write!(f, "{a}e+00{b}")
    } else if num_abs <= 1e-100 {
        write!(f, "{num:>14.6e}, ")
    } else if num_abs >= 1e100 {
        let temp_1 = format!("{num:>13.6e}, ").to_string();
        let mut temp_2 = temp_1.split("e");
        let a = temp_2.next().unwrap();
        let b = temp_2.next().unwrap();
        write!(f, "{a}e+{b}")
    } else if num_abs <= 1e-10 {
        let temp_1 = format!("{num:>13.6e}, ").to_string();
        let mut temp_2 = temp_1.split("e");
        let a = temp_2.next().unwrap();
        let b = temp_2.next().unwrap();
        let mut c = b.split("-");
        c.next();
        let e = c.next().unwrap();
        write!(f, "{a}e-0{e}")
    } else if num_abs >= 1e10 {
        let temp_1 = format!("{num:>12.6e}, ").to_string();
        let mut temp_2 = temp_1.split("e");
        let a = temp_2.next().unwrap();
        let b = temp_2.next().unwrap();
        write!(f, "{a}e+0{b}")
    } else if num_abs <= 1e0 {
        let temp_1 = format!("{num:>12.6e}, ").to_string();
        let mut temp_2 = temp_1.split("e");
        let a = temp_2.next().unwrap();
        let b = temp_2.next().unwrap();
        let mut c = b.split("-");
        c.next();
        let e = c.next().unwrap();
        write!(f, "{a}e-00{e}")
    } else {
        let temp_1 = format!("{num:>11.6e}, ").to_string();
        let mut temp_2 = temp_1.split("e");
        let a = temp_2.next().unwrap();
        let b = temp_2.next().unwrap();
        write!(f, "{a}e+00{b}")
    }
}
