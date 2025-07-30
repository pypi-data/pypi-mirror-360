//! This module provides a way to correct events for various effects, such as pedestal bias.
//!
//!
//! Types of corrections:
//! - [`Pedestals`]
//!
//! An iterator extension is provided to correct events in an iterator.

pub use pedestals::Pedestals;

use crate::{acquisition::Params, CalibrationError, Event};

mod pedestals;

/// Builder for applying corrections to events.
///
/// For now only pedestals are supported.
#[derive(Debug, Clone)]
pub struct Corrections {
    params: Params,
    pedestals: Option<Pedestals>,
}

impl Corrections {
    pub fn new(params: Params) -> Self {
        Self {
            params,
            pedestals: None,
        }
    }

    /// Set the pedestals to use for correction.
    pub fn pedestals(mut self, pedestals: Option<Pedestals>) -> Self {
        self.pedestals = pedestals;
        self
    }
}

/// An iterator which applies corrections to [`Event`] objects.
///
/// This iterator is created using the `corrected` method on `Iterator<Item = E>` where `E: Event`.
pub struct Corrected<I, E>
where
    I: Iterator<Item = E>,
    E: Event,
{
    iter: I,
    corrections: Corrections,
}

impl<I, E> Iterator for Corrected<I, E>
where
    I: Iterator<Item = E>,
    E: Event,
{
    type Item = Result<E, CalibrationError>;

    fn next(&mut self) -> Option<Self::Item> {
        let mut event = self.iter.next()?.clone();
        let corrections = &self.corrections;

        if let Some(ref peds) = corrections.pedestals {
            match peds.correct(&mut event, &corrections.params) {
                Ok(_) => Some(Ok(event)),
                Err(err) => Some(Err(err)),
            }
        } else {
            Some(Ok(event))
        }
    }
}

/// Extension trait for the [`Corrected`] iterator type.
pub trait CorrectedExt<E>: Iterator<Item = E> + Sized
where
    E: Event,
{
    /// Iterate over corrected events.
    ///
    /// The given [`Corrections`] are applied to each event.
    fn corrected(self, corrections: Corrections) -> Corrected<Self, E> {
        Corrected {
            iter: self,
            corrections,
        }
    }
}

impl<I, E> CorrectedExt<E> for I
where
    I: Iterator<Item = E>,
    E: Event,
{
}
