#[cfg(test)]
mod test;

use crate::{
    constitutive::{
        Constitutive, ConstitutiveError, Parameters,
        solid::{FIVE_THIRDS, Solid, TWO_THIRDS, elastic::Elastic, hyperelastic::Hyperelastic},
    },
    math::{IDENTITY, Rank2},
    mechanics::{CauchyStress, CauchyTangentStiffness, Deformation, DeformationGradient, Scalar},
};

#[doc = include_str!("model.md")]
#[derive(Debug)]
pub struct MooneyRivlin<P> {
    parameters: P,
}

impl<P> MooneyRivlin<P>
where
    P: Parameters,
{
    /// Returns the extra modulus.
    pub fn extra_modulus(&self) -> &Scalar {
        self.parameters.get(2)
    }
}

impl<P> Constitutive<P> for MooneyRivlin<P>
where
    P: Parameters,
{
    fn new(parameters: P) -> Self {
        Self { parameters }
    }
}

impl<P> Solid for MooneyRivlin<P>
where
    P: Parameters,
{
    fn bulk_modulus(&self) -> &Scalar {
        self.parameters.get(0)
    }
    fn shear_modulus(&self) -> &Scalar {
        self.parameters.get(1)
    }
}

impl<P> Elastic for MooneyRivlin<P>
where
    P: Parameters,
{
    #[doc = include_str!("cauchy_stress.md")]
    fn cauchy_stress(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<CauchyStress, ConstitutiveError> {
        let jacobian = self.jacobian(deformation_gradient)?;
        let isochoric_left_cauchy_green_deformation =
            deformation_gradient.left_cauchy_green() / jacobian.powf(TWO_THIRDS);
        Ok(((isochoric_left_cauchy_green_deformation.deviatoric()
            * (self.shear_modulus() - self.extra_modulus())
            - isochoric_left_cauchy_green_deformation
                .inverse()
                .deviatoric()
                * self.extra_modulus())
            + IDENTITY * (self.bulk_modulus() * 0.5 * (jacobian.powi(2) - 1.0)))
            / jacobian)
    }
    #[doc = include_str!("cauchy_tangent_stiffness.md")]
    fn cauchy_tangent_stiffness(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<CauchyTangentStiffness, ConstitutiveError> {
        let jacobian = self.jacobian(deformation_gradient)?;
        let inverse_transpose_deformation_gradient = deformation_gradient.inverse_transpose();
        let scaled_delta_shear_modulus =
            (self.shear_modulus() - self.extra_modulus()) / jacobian.powf(FIVE_THIRDS);
        let inverse_isochoric_left_cauchy_green_deformation =
            (deformation_gradient.left_cauchy_green() / jacobian.powf(TWO_THIRDS)).inverse();
        let deviatoric_inverse_isochoric_left_cauchy_green_deformation =
            inverse_isochoric_left_cauchy_green_deformation.deviatoric();
        let term_1 = CauchyTangentStiffness::dyad_ij_kl(
            &inverse_isochoric_left_cauchy_green_deformation,
            &inverse_transpose_deformation_gradient,
        ) * TWO_THIRDS
            - CauchyTangentStiffness::dyad_ik_jl(
                &inverse_isochoric_left_cauchy_green_deformation,
                &inverse_transpose_deformation_gradient,
            )
            - CauchyTangentStiffness::dyad_il_jk(
                &inverse_transpose_deformation_gradient,
                &inverse_isochoric_left_cauchy_green_deformation,
            );
        let term_3 = CauchyTangentStiffness::dyad_ij_kl(
            &deviatoric_inverse_isochoric_left_cauchy_green_deformation,
            &inverse_transpose_deformation_gradient,
        );
        let term_2 = CauchyTangentStiffness::dyad_ij_kl(
            &IDENTITY,
            &((deviatoric_inverse_isochoric_left_cauchy_green_deformation * TWO_THIRDS)
                * &inverse_transpose_deformation_gradient),
        );
        Ok(
            (CauchyTangentStiffness::dyad_ik_jl(&IDENTITY, deformation_gradient)
                + CauchyTangentStiffness::dyad_il_jk(deformation_gradient, &IDENTITY)
                - CauchyTangentStiffness::dyad_ij_kl(&IDENTITY, deformation_gradient)
                    * (TWO_THIRDS))
                * scaled_delta_shear_modulus
                + CauchyTangentStiffness::dyad_ij_kl(
                    &(IDENTITY * (0.5 * self.bulk_modulus() * (jacobian + 1.0 / jacobian))
                        - deformation_gradient.left_cauchy_green().deviatoric()
                            * (scaled_delta_shear_modulus * FIVE_THIRDS)),
                    &inverse_transpose_deformation_gradient,
                )
                - (term_1 + term_2 - term_3) * self.extra_modulus() / jacobian,
        )
    }
}

impl<P> Hyperelastic for MooneyRivlin<P>
where
    P: Parameters,
{
    #[doc = include_str!("helmholtz_free_energy_density.md")]
    fn helmholtz_free_energy_density(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<Scalar, ConstitutiveError> {
        let jacobian = self.jacobian(deformation_gradient)?;
        let isochoric_left_cauchy_green_deformation =
            deformation_gradient.left_cauchy_green() / jacobian.powf(TWO_THIRDS);
        Ok(0.5
            * ((self.shear_modulus() - self.extra_modulus())
                * (isochoric_left_cauchy_green_deformation.trace() - 3.0)
                + self.extra_modulus()
                    * (isochoric_left_cauchy_green_deformation.second_invariant() - 3.0)
                + self.bulk_modulus() * (0.5 * (jacobian.powi(2) - 1.0) - jacobian.ln())))
    }
}
