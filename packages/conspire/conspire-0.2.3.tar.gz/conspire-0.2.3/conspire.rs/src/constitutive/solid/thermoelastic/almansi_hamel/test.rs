use super::super::test::*;
use super::*;

type AlmansiHamelType<'a> = AlmansiHamel<&'a [Scalar; 4]>;

test_solid_thermoelastic_constitutive_model!(
    AlmansiHamelType,
    ALMANSIHAMELPARAMETERS,
    AlmansiHamel::new(ALMANSIHAMELPARAMETERS)
);

mod consistency {
    use super::*;
    use crate::{
        constitutive::solid::elastic::{
            AlmansiHamel as ElasticAlmansiHamel, Elastic,
            test::ALMANSIHAMELPARAMETERS as ELASTICALMANSIHAMELPARAMETERS,
        },
        math::test::assert_eq_within_tols,
    };
    #[test]
    fn cauchy_stress() -> Result<(), TestError> {
        let model = AlmansiHamel::new(ALMANSIHAMELPARAMETERS);
        let elastic_model = ElasticAlmansiHamel::new(ELASTICALMANSIHAMELPARAMETERS);
        assert_eq_within_tols(
            &model.cauchy_stress(&get_deformation_gradient(), model.reference_temperature())?,
            &elastic_model.cauchy_stress(&get_deformation_gradient())?,
        )
    }
    #[test]
    fn cauchy_tangent_stiffness() -> Result<(), TestError> {
        let model = AlmansiHamel::new(ALMANSIHAMELPARAMETERS);
        let elastic_model = ElasticAlmansiHamel::new(ELASTICALMANSIHAMELPARAMETERS);
        assert_eq_within_tols(
            &model.cauchy_tangent_stiffness(
                &get_deformation_gradient(),
                model.reference_temperature(),
            )?,
            &elastic_model.cauchy_tangent_stiffness(&get_deformation_gradient())?,
        )
    }
}
