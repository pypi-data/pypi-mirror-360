use super::*;
use crate::constitutive::solid::thermohyperelastic::{
    SaintVenantKirchhoff, test::SAINTVENANTKIRCHOFFPARAMETERS,
};

type SaintVenantKirchhoffType<'a> = SaintVenantKirchhoff<&'a [Scalar; 4]>;
type FourierType<'a> = Fourier<&'a [Scalar; 1]>;

test_thermohyperelastic_thermal_conduction_constitutive_model!(
    SaintVenantKirchhoffType,
    SAINTVENANTKIRCHOFFPARAMETERS,
    FourierType,
    FOURIERPARAMETERS
);

macro_rules! test_thermohyperelastic_thermal_conduction_constitutive_model
{
    ($thermohyperelastic_constitutive_model: ident, $thermohyperelastic_constitutive_model_parameters: expr,
     $thermal_conduction_constitutive_model: ident, $thermal_conduction_constitutive_model_parameters: expr) =>
    {
        use crate::{
            constitutive::multiphysics::solid_thermal::thermoelastic_thermal_conduction::test::test_thermoelastic_thermal_conduction_constitutive_model,
            math::test::{assert_eq, TestError}
        };
        test_thermoelastic_thermal_conduction_constitutive_model!(
            ThermohyperelasticThermalConduction,
            $thermohyperelastic_constitutive_model, $thermohyperelastic_constitutive_model_parameters,
            $thermal_conduction_constitutive_model, $thermal_conduction_constitutive_model_parameters
        );
        #[test]
        fn helmholtz_free_energy_density() -> Result<(), TestError>
        {
            assert_eq(
                &get_thermoelastic_thermal_conduction_constitutive_model()
                .helmholtz_free_energy_density(
                    &get_deformation_gradient(), &get_temperature()
                )?,
                &get_thermoelastic_constitutive_model()
                .helmholtz_free_energy_density(
                    &get_deformation_gradient(), &get_temperature()
                )?
            )
        }
    }
}
pub(crate) use test_thermohyperelastic_thermal_conduction_constitutive_model;
