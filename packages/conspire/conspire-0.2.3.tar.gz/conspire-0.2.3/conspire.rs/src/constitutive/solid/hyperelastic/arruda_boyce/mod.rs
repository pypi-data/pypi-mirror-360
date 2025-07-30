#[cfg(test)]
mod test;

use crate::{
    constitutive::{
        Constitutive, ConstitutiveError, Parameters,
        solid::{FIVE_THIRDS, Solid, TWO_THIRDS, elastic::Elastic, hyperelastic::Hyperelastic},
    },
    math::{
        IDENTITY, Rank2,
        special::{inverse_langevin, langevin_derivative},
    },
    mechanics::{CauchyStress, CauchyTangentStiffness, Deformation, DeformationGradient, Scalar},
};

#[doc = include_str!("model.md")]
#[derive(Debug)]
pub struct ArrudaBoyce<P> {
    parameters: P,
}

impl<P> ArrudaBoyce<P>
where
    P: Parameters,
{
    /// Returns the number of links.
    pub fn number_of_links(&self) -> &Scalar {
        self.parameters.get(2)
    }
}

impl<P> Constitutive<P> for ArrudaBoyce<P>
where
    P: Parameters,
{
    fn new(parameters: P) -> Self {
        Self { parameters }
    }
}

impl<P> Solid for ArrudaBoyce<P>
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

impl<P> Elastic for ArrudaBoyce<P>
where
    P: Parameters,
{
    #[doc = include_str!("cauchy_stress.md")]
    fn cauchy_stress(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<CauchyStress, ConstitutiveError> {
        let jacobian = self.jacobian(deformation_gradient)?;
        let (
            deviatoric_isochoric_left_cauchy_green_deformation,
            isochoric_left_cauchy_green_deformation_trace,
        ) = (deformation_gradient.left_cauchy_green() / jacobian.powf(TWO_THIRDS))
            .deviatoric_and_trace();
        let gamma =
            (isochoric_left_cauchy_green_deformation_trace / 3.0 / self.number_of_links()).sqrt();
        if gamma >= 1.0 {
            Err(ConstitutiveError::Custom(
                "Maximum extensibility reached.".to_string(),
                deformation_gradient.clone(),
                format!("{:?}", &self),
            ))
        } else {
            let gamma_0 = (1.0 / self.number_of_links()).sqrt();
            Ok(deviatoric_isochoric_left_cauchy_green_deformation
                * (self.shear_modulus() * inverse_langevin(gamma) / inverse_langevin(gamma_0)
                    * gamma_0
                    / gamma
                    / jacobian)
                + IDENTITY * self.bulk_modulus() * 0.5 * (jacobian - 1.0 / jacobian))
        }
    }
    #[doc = include_str!("cauchy_tangent_stiffness.md")]
    fn cauchy_tangent_stiffness(
        &self,
        deformation_gradient: &DeformationGradient,
    ) -> Result<CauchyTangentStiffness, ConstitutiveError> {
        let jacobian = self.jacobian(deformation_gradient)?;
        let inverse_transpose_deformation_gradient = deformation_gradient.inverse_transpose();
        let left_cauchy_green_deformation = deformation_gradient.left_cauchy_green();
        let deviatoric_left_cauchy_green_deformation = left_cauchy_green_deformation.deviatoric();
        let (
            deviatoric_isochoric_left_cauchy_green_deformation,
            isochoric_left_cauchy_green_deformation_trace,
        ) = (left_cauchy_green_deformation / jacobian.powf(TWO_THIRDS)).deviatoric_and_trace();
        let gamma =
            (isochoric_left_cauchy_green_deformation_trace / 3.0 / self.number_of_links()).sqrt();
        if gamma >= 1.0 {
            Err(ConstitutiveError::Custom(
                "Maximum extensibility reached.".to_string(),
                deformation_gradient.clone(),
                format!("{:?}", &self),
            ))
        } else {
            let gamma_0 = (1.0 / self.number_of_links()).sqrt();
            let eta = inverse_langevin(gamma);
            let scaled_shear_modulus =
                gamma_0 / inverse_langevin(gamma_0) * self.shear_modulus() * eta
                    / gamma
                    / jacobian.powf(FIVE_THIRDS);
            let scaled_deviatoric_isochoric_left_cauchy_green_deformation =
                deviatoric_left_cauchy_green_deformation * scaled_shear_modulus;
            let term = CauchyTangentStiffness::dyad_ij_kl(
                &scaled_deviatoric_isochoric_left_cauchy_green_deformation,
                &(deviatoric_isochoric_left_cauchy_green_deformation
                    * &inverse_transpose_deformation_gradient
                    * ((1.0 / eta / langevin_derivative(eta) - 1.0 / gamma)
                        / 3.0
                        / self.number_of_links()
                        / gamma)),
            );
            Ok(
                (CauchyTangentStiffness::dyad_ik_jl(&IDENTITY, deformation_gradient)
                    + CauchyTangentStiffness::dyad_il_jk(deformation_gradient, &IDENTITY)
                    - CauchyTangentStiffness::dyad_ij_kl(&IDENTITY, deformation_gradient)
                        * (TWO_THIRDS))
                    * scaled_shear_modulus
                    + CauchyTangentStiffness::dyad_ij_kl(
                        &(IDENTITY * (0.5 * self.bulk_modulus() * (jacobian + 1.0 / jacobian))
                            - scaled_deviatoric_isochoric_left_cauchy_green_deformation
                                * (FIVE_THIRDS)),
                        &inverse_transpose_deformation_gradient,
                    )
                    + term,
            )
        }
    }
}

impl<P> Hyperelastic for ArrudaBoyce<P>
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
        let gamma =
            (isochoric_left_cauchy_green_deformation.trace() / 3.0 / self.number_of_links()).sqrt();
        if gamma >= 1.0 {
            Err(ConstitutiveError::Custom(
                "Maximum extensibility reached.".to_string(),
                deformation_gradient.clone(),
                format!("{:?}", &self),
            ))
        } else {
            let eta = inverse_langevin(gamma);
            let gamma_0 = (1.0 / self.number_of_links()).sqrt();
            let eta_0 = inverse_langevin(gamma_0);
            Ok(3.0 * gamma_0 / eta_0
                * self.shear_modulus()
                * self.number_of_links()
                * (gamma * eta
                    - gamma_0 * eta_0
                    - (eta_0 * eta.sinh() / (eta * eta_0.sinh())).ln())
                + 0.5 * self.bulk_modulus() * (0.5 * (jacobian.powi(2) - 1.0) - jacobian.ln()))
        }
    }
}
