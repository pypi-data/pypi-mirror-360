//! Thermohyperelastic constitutive models.

#[cfg(test)]
pub mod test;

mod saint_venant_kirchhoff;

pub use saint_venant_kirchhoff::SaintVenantKirchhoff;

use super::{thermoelastic::Thermoelastic, *};

/// Required methods for thermohyperelastic constitutive models.
pub trait Thermohyperelastic
where
    Self: Thermoelastic,
{
    /// Calculates and returns the Helmholtz free energy density.
    ///
    /// ```math
    /// a = a(\mathbf{F},T)
    /// ```
    fn helmholtz_free_energy_density(
        &self,
        deformation_gradient: &DeformationGradient,
        temperature: &Scalar,
    ) -> Result<Scalar, ConstitutiveError>;
}
