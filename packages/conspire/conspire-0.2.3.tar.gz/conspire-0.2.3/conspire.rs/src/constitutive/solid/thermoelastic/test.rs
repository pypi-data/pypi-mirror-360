use crate::{
    constitutive::solid::elastic::test::ALMANSIHAMELPARAMETERS as ALMANSIHAMELPARAMETERSELASTIC,
    mechanics::Scalar,
};
pub const ALMANSIHAMELPARAMETERS: &[Scalar; 4] = &[
    ALMANSIHAMELPARAMETERSELASTIC[0],
    ALMANSIHAMELPARAMETERSELASTIC[1],
    1.0,
    100.0,
];

macro_rules! cauchy_stress_from_deformation_gradient {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed.cauchy_stress($deformation_gradient, &get_temperature())
    };
}
pub(crate) use cauchy_stress_from_deformation_gradient;

macro_rules! cauchy_stress_from_deformation_gradient_simple {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed.cauchy_stress(
            $deformation_gradient,
            $constitutive_model_constructed.reference_temperature(),
        )
    };
}
pub(crate) use cauchy_stress_from_deformation_gradient_simple;

macro_rules! cauchy_stress_from_deformation_gradient_rotated {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed.cauchy_stress($deformation_gradient, &get_temperature())
    };
}
pub(crate) use cauchy_stress_from_deformation_gradient_rotated;

macro_rules! cauchy_tangent_stiffness_from_deformation_gradient {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed
            .cauchy_tangent_stiffness($deformation_gradient, &get_temperature())
    };
}
pub(crate) use cauchy_tangent_stiffness_from_deformation_gradient;

macro_rules! first_piola_kirchhoff_stress_from_deformation_gradient {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed
            .first_piola_kirchhoff_stress($deformation_gradient, &get_temperature())
    };
}
pub(crate) use first_piola_kirchhoff_stress_from_deformation_gradient;

macro_rules! first_piola_kirchhoff_stress_from_deformation_gradient_simple {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed.first_piola_kirchhoff_stress(
            $deformation_gradient,
            $constitutive_model_constructed.reference_temperature(),
        )
    };
}
pub(crate) use first_piola_kirchhoff_stress_from_deformation_gradient_simple;

macro_rules! first_piola_kirchhoff_stress_from_deformation_gradient_rotated {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed
            .first_piola_kirchhoff_stress($deformation_gradient, &get_temperature())
    };
}
pub(crate) use first_piola_kirchhoff_stress_from_deformation_gradient_rotated;

macro_rules! first_piola_kirchhoff_tangent_stiffness_from_deformation_gradient {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed
            .first_piola_kirchhoff_tangent_stiffness($deformation_gradient, &get_temperature())
    };
}
pub(crate) use first_piola_kirchhoff_tangent_stiffness_from_deformation_gradient;

macro_rules! first_piola_kirchhoff_tangent_stiffness_from_deformation_gradient_simple {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed.first_piola_kirchhoff_tangent_stiffness(
            $deformation_gradient,
            &$constitutive_model_constructed.reference_temperature(),
        )
    };
}
pub(crate) use first_piola_kirchhoff_tangent_stiffness_from_deformation_gradient_simple;

macro_rules! second_piola_kirchhoff_stress_from_deformation_gradient {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed
            .second_piola_kirchhoff_stress($deformation_gradient, &get_temperature())
    };
}
pub(crate) use second_piola_kirchhoff_stress_from_deformation_gradient;

macro_rules! second_piola_kirchhoff_stress_from_deformation_gradient_simple {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed.second_piola_kirchhoff_stress(
            $deformation_gradient,
            $constitutive_model_constructed.reference_temperature(),
        )
    };
}
pub(crate) use second_piola_kirchhoff_stress_from_deformation_gradient_simple;

macro_rules! second_piola_kirchhoff_stress_from_deformation_gradient_rotated {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed
            .second_piola_kirchhoff_stress($deformation_gradient, &get_temperature())
    };
}
pub(crate) use second_piola_kirchhoff_stress_from_deformation_gradient_rotated;

macro_rules! second_piola_kirchhoff_tangent_stiffness_from_deformation_gradient {
    ($constitutive_model_constructed: expr, $deformation_gradient: expr) => {
        $constitutive_model_constructed
            .second_piola_kirchhoff_tangent_stiffness($deformation_gradient, &get_temperature())
    };
}
pub(crate) use second_piola_kirchhoff_tangent_stiffness_from_deformation_gradient;

macro_rules! test_solid_thermal_constitutive_model {
    ($constitutive_model: ident, $constitutive_model_parameters: expr, $constitutive_model_constructed: expr) => {
        use crate::mechanics::test::get_temperature;
        fn get_thermoelastic_constitutive_model<'a>() -> $constitutive_model<'a> {
            $constitutive_model::new($constitutive_model_parameters)
        }
        #[test]
        fn get_coefficient_of_thermal_expansion() {
            assert_eq!(
                &$constitutive_model_parameters[2],
                get_thermoelastic_constitutive_model().coefficient_of_thermal_expansion()
            )
        }
        #[test]
        fn get_reference_temperature() {
            assert_eq!(
                &$constitutive_model_parameters[3],
                get_thermoelastic_constitutive_model().reference_temperature()
            )
        }
        #[test]
        fn coefficient_of_thermal_expansion() -> Result<(), TestError> {
            let model = get_thermoelastic_constitutive_model();
            let deformation_gradient = DeformationGradient::identity();
            let temperature = model.reference_temperature() - crate::EPSILON;
            let first_piola_kirchhoff_stress =
                model.first_piola_kirchhoff_stress(&deformation_gradient, &temperature)?;
            let compare = 3.0 * model.bulk_modulus() * crate::EPSILON;
            (0..3).try_for_each(|i| {
                (0..3).try_for_each(|j| {
                    if i == j {
                        assert!(
                            (first_piola_kirchhoff_stress[i][j] / compare
                                - model.coefficient_of_thermal_expansion())
                            .abs()
                                < crate::EPSILON
                        );
                        Ok(())
                    } else {
                        assert_eq(&first_piola_kirchhoff_stress[i][j], &0.0)
                    }
                })
            })
        }
    };
}
pub(crate) use test_solid_thermal_constitutive_model;

macro_rules! test_solid_thermoelastic_constitutive_model {
    ($constitutive_model: ident, $constitutive_model_parameters: expr, $constitutive_model_constructed: expr) => {
        crate::constitutive::solid::elastic::test::test_solid_elastic_constitutive_model!(
            $constitutive_model,
            $constitutive_model_parameters,
            $constitutive_model_constructed
        );
        crate::constitutive::solid::thermoelastic::test::test_solid_thermal_constitutive_model!(
            $constitutive_model,
            $constitutive_model_parameters,
            $constitutive_model_constructed
        );
    };
}
pub(crate) use test_solid_thermoelastic_constitutive_model;
