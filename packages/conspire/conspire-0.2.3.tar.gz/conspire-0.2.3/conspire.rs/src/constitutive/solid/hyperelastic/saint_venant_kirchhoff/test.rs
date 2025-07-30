use super::super::test::*;
use super::*;
use crate::mechanics::CauchyTangentStiffness;

type SaintVenantKirchhoffType<'a> = SaintVenantKirchhoff<&'a [Scalar; 2]>;

use_elastic_macros!();

test_solid_hyperelastic_constitutive_model!(
    SaintVenantKirchhoffType,
    SAINTVENANTKIRCHOFFPARAMETERS,
    SaintVenantKirchhoff::new(SAINTVENANTKIRCHOFFPARAMETERS)
);

test_minimize!(SaintVenantKirchhoff::new(SAINTVENANTKIRCHOFFPARAMETERS));
test_solve!(SaintVenantKirchhoff::new(SAINTVENANTKIRCHOFFPARAMETERS));
