use crate::impl_macros::macros::*;
use crate::prelude::*;
use crate::quantities::*;
use ndarray::{Array1, Array2, ArrayView1, ArrayView2};
use num_traits::identities::Zero;
use num_traits::FromPrimitive;
#[cfg(feature = "pyo3")]
use pyo3::pyclass;
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::fmt;
use std::ops::{Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Sub, SubAssign};

#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Copy, Clone, PartialEq, Debug)]
#[cfg_attr(feature = "pyo3", pyclass(eq, eq_int))]
pub enum ForcePerVolumeUnit {
    N_mcb,
    N_mmcb,
}

impl PhysicsUnit for ForcePerVolumeUnit {
    fn name(&self) -> &str {
        match &self {
            ForcePerVolumeUnit::N_mcb => "N/m³",
            ForcePerVolumeUnit::N_mmcb => "N/mm³",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            ForcePerVolumeUnit::N_mcb => (1., 0),
            ForcePerVolumeUnit::N_mmcb => (1., 9),
        }
    }
}

impl_quantity!(
    ForcePerVolume,
    ForcePerVolumeUnit,
    ForcePerVolumeUnit::N_mcb
);
impl_div_with_self_to_f64!(ForcePerVolume);
impl_div!(Force, Volume, ForcePerVolume);
impl_mul!(ForcePerVolume, Volume, Force);
impl_mul!(Density, Acceleration, ForcePerVolume);
impl_mul!(ForcePerVolume, Area, MassPerTimeSquare);
impl_mul!(ForcePerVolume, Distance, MassPerDistanceTimeSquare);
impl_mul!(ForcePerVolume, InverseDistance, ForcePerDistancePowerFour);
impl_div!(ForcePerVolume, Density, Acceleration);
impl_div!(ForcePerVolume, Acceleration, Density);
