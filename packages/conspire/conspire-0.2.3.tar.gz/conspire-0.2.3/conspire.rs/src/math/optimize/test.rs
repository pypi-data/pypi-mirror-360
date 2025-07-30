use super::{
    super::{Scalar, Tensor, special, test::TestError},
    OptimizeError,
};

pub fn rosenbrock<T>(x: &T) -> Result<Scalar, OptimizeError>
where
    T: Tensor<Item = Scalar>,
{
    Ok(special::rosenbrock(x, 1.0, 100.0))
}

pub fn rosenbrock_derivative<T>(x: &T) -> Result<T, OptimizeError>
where
    T: FromIterator<Scalar> + Tensor<Item = Scalar>,
{
    Ok(special::rosenbrock_derivative(x, 1.0, 100.0))
}

// pub fn rosenbrock_second_derivative<T, U>(x: &T) -> Result<U, OptimizeError>
// where
//     T: FromIterator<Scalar> + Tensor<Item = Scalar>,
//     U: Tensor<Item = T>,
// {
//     Ok(special::rosenbrock_second_derivative(x, 1.0, 100.0))
// }

#[test]
fn debug() {
    let _ = format!(
        "{:?}",
        OptimizeError::MaximumStepsReached(1, "foo".to_string())
    );
    let _ = format!(
        "{:?}",
        OptimizeError::NotMinimum("foo".to_string(), "bar".to_string())
    );
}

#[test]
fn display() {
    let _ = format!(
        "{}",
        OptimizeError::MaximumStepsReached(1, "foo".to_string())
    );
    let _ = format!(
        "{}",
        OptimizeError::NotMinimum("foo".to_string(), "bar".to_string())
    );
}

#[test]
fn into_test_error() {
    let optimize_error = OptimizeError::MaximumStepsReached(1, "foo".to_string());
    let _: TestError = optimize_error.into();
}
