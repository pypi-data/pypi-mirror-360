#[cfg(test)]
mod test;

use crate::{
    ABS_TOL,
    constitutive::{
        ConstitutiveError,
        hybrid::{Hybrid, Multiplicative, MultiplicativeTrait},
        solid::{Solid, elastic::Elastic},
    },
    math::{IDENTITY_10, Rank2, Tensor, TensorRank2, ZERO_10},
    mechanics::{
        CauchyStress, CauchyTangentStiffness, DeformationGradient, FirstPiolaKirchhoffStress,
        FirstPiolaKirchhoffTangentStiffness, Scalar, SecondPiolaKirchhoffStress,
        SecondPiolaKirchhoffTangentStiffness,
    },
};

impl<C1, C2> Solid for Multiplicative<C1, C2> {
    /// Dummy method that will panic.
    fn bulk_modulus(&self) -> &Scalar {
        panic!()
    }
    /// Dummy method that will panic.
    fn shear_modulus(&self) -> &Scalar {
        panic!()
    }
}

impl<C1, C2> Elastic for Multiplicative<C1, C2>
where
    C1: Elastic,
    C2: Elastic,
{
    /// Calculates and returns the Cauchy stress.
    ///
    /// ```math
    /// \boldsymbol{\sigma}(\mathbf{F}) = \frac{1}{J_2}\,\boldsymbol{\sigma}_1(\mathbf{F}_1)
    /// ```
    fn cauchy_stress(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<CauchyStress, ConstitutiveError> {
        let (deformation_gradient_1, deformation_gradient_2) =
            self.deformation_gradients(deformation_gradient)?;
        Ok(self
            .constitutive_model_1()
            .cauchy_stress(&deformation_gradient_1)?
            / deformation_gradient_2.determinant())
    }
    /// Dummy method that will panic.
    fn cauchy_tangent_stiffness(
        &self,
        _: &DeformationGradient,
    ) -> Result<CauchyTangentStiffness, ConstitutiveError> {
        panic!()
    }
    /// Calculates and returns the first Piola-Kirchhoff stress.
    ///
    /// ```math
    /// \mathbf{P}(\mathbf{F}) = \mathbf{P}_1(\mathbf{F}_1)\cdot\mathbf{F}_2^{-T}
    /// ```
    fn first_piola_kirchhoff_stress(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<FirstPiolaKirchhoffStress, ConstitutiveError> {
        let (deformation_gradient_1, deformation_gradient_2) =
            self.deformation_gradients(deformation_gradient)?;
        let deformation_gradient_2_inverse_transpose: TensorRank2<3, 0, 0> =
            deformation_gradient_2.inverse_transpose().into();
        Ok(self
            .constitutive_model_1()
            .first_piola_kirchhoff_stress(&deformation_gradient_1)?
            * deformation_gradient_2_inverse_transpose)
    }
    /// Dummy method that will panic.
    fn first_piola_kirchhoff_tangent_stiffness(
        &self,
        _: &DeformationGradient,
    ) -> Result<FirstPiolaKirchhoffTangentStiffness, ConstitutiveError> {
        panic!()
    }
    /// Calculates and returns the second Piola-Kirchhoff stress.
    ///
    /// ```math
    /// \mathbf{S}(\mathbf{F}) = \mathbf{F}_2^{-1}\cdot\mathbf{S}_1(\mathbf{F}_1)\cdot\mathbf{F}_2^{-T}
    /// ```
    fn second_piola_kirchhoff_stress(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<SecondPiolaKirchhoffStress, ConstitutiveError> {
        let (deformation_gradient_1, deformation_gradient_2) =
            self.deformation_gradients(deformation_gradient)?;
        let deformation_gradient_2_inverse: TensorRank2<3, 0, 0> =
            deformation_gradient_2.inverse().into();
        Ok(&deformation_gradient_2_inverse
            * self
                .constitutive_model_1()
                .second_piola_kirchhoff_stress(&deformation_gradient_1)?
            * deformation_gradient_2_inverse.transpose())
    }
    /// Dummy method that will panic.
    fn second_piola_kirchhoff_tangent_stiffness(
        &self,
        _: &DeformationGradient,
    ) -> Result<SecondPiolaKirchhoffTangentStiffness, ConstitutiveError> {
        panic!()
    }
}

impl<C1, C2> MultiplicativeTrait for Multiplicative<C1, C2>
where
    C1: Elastic,
    C2: Elastic,
{
    fn deformation_gradients(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<(DeformationGradient, DeformationGradient), ConstitutiveError> {
        if deformation_gradient.is_identity() {
            Ok((IDENTITY_10, IDENTITY_10))
        } else {
            let mut deformation_gradient_1 = IDENTITY_10;
            let mut deformation_gradient_2 = deformation_gradient.clone();
            let mut deformation_gradient_2_old = IDENTITY_10;
            let mut deformation_gradient_2_inverse_transpose: TensorRank2<3, 0, 0>;
            let mut residual: FirstPiolaKirchhoffStress;
            let mut residual_increment: FirstPiolaKirchhoffStress;
            let mut residual_norm = 1.0;
            let mut residual_old = ZERO_10;
            let mut right_hand_side: FirstPiolaKirchhoffStress;
            let mut steps: u8 = 0;
            let steps_maximum: u8 = 50;
            let mut step_size: Scalar;
            while steps < steps_maximum {
                deformation_gradient_1 =
                    (deformation_gradient * deformation_gradient_2.inverse()).into();
                deformation_gradient_2_inverse_transpose =
                    deformation_gradient_2.inverse_transpose().into();
                right_hand_side = (deformation_gradient_1.transpose()
                    * self
                        .constitutive_model_1()
                        .first_piola_kirchhoff_stress(&deformation_gradient_1)?
                    * deformation_gradient_2_inverse_transpose)
                    .into();
                residual = self
                    .constitutive_model_2()
                    .first_piola_kirchhoff_stress(&deformation_gradient_2)?
                    - right_hand_side;
                residual_norm = residual.norm();
                if residual_norm >= ABS_TOL {
                    residual_increment = residual_old - &residual;
                    step_size = (deformation_gradient_2_old - &deformation_gradient_2)
                        .full_contraction(&residual_increment)
                        .abs()
                        / residual_increment.norm_squared();
                    deformation_gradient_2_old = deformation_gradient_2.clone();
                    residual_old = residual.clone();
                    deformation_gradient_2 -= residual * step_size;
                } else {
                    break;
                }
                steps += 1;
            }
            if residual_norm >= ABS_TOL && steps == steps_maximum {
                panic!("MAX STEPS REACHED")
            } else {
                Ok((deformation_gradient_1, deformation_gradient_2))
            }
        }
    }
}
