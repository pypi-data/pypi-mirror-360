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
pub enum MassPerDistanceTimeSquareUnit {
    kg_mssq,
}

impl PhysicsUnit for MassPerDistanceTimeSquareUnit {
    fn name(&self) -> &str {
        match &self {
            MassPerDistanceTimeSquareUnit::kg_mssq => "kg/ms²",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            MassPerDistanceTimeSquareUnit::kg_mssq => (1., 0),
        }
    }
}

impl_quantity!(
    MassPerDistanceTimeSquare,
    MassPerDistanceTimeSquareUnit,
    MassPerDistanceTimeSquareUnit::kg_mssq
);
impl_div_with_self_to_f64!(MassPerDistanceTimeSquare);

impl_div!(MassPerDistanceTimeSquare, Distance, ForcePerVolume);
impl_div!(MassPerDistanceTimeSquare, ForcePerVolume, Distance);
impl_mul!(MassPerDistanceTimeSquare, Distance, MassPerTimeSquare);
