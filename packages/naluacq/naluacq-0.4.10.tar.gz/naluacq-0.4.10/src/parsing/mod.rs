//! This module provides concrete implementations of the [`Event`] trait for events
//! for each supported data format:
//!
//! - [AARDVARCv3](Aardvarcv3Event)
//! - [AODSoC](AodsocEvent)
//! - [AODSv2](Aodsv2Event)
//! - [ASoCv3](Asocv3Event)
//! - [ASoCv3S](Asocv3SEvent)
//! - [HDSoCv1](Hdsocv1Event)
//! - [TRBHMv1](Trbhmv1Event)
//! - [UDC16](Udc16Event)
//! - [UPAC96](Upac96Event)
//!
//! These concrete implementations are obtained by parsing raw bytes into the corresponding
//! event type. The [`ParseInto`] trait is implemented for `Deref<Target=[u8]>` which allows for
//! parsing `[u8]`, `Vec<u8>`, etc.

use crate::{acquisition::Params, error::ParsingError, Event};

pub use aardvarcv3::Aardvarcv3Event;
pub use aodsoc::AodsocEvent;
pub use aodsv2::Aodsv2Event;
pub use asocv3::Asocv3Event;
pub use asocv3s::Asocv3SEvent;
pub use hdsocv1::Hdsocv1Event;
pub use trbhmv1::Trbhmv1Event;
pub use udc16::Udc16Event;
pub use upac96::Upac96Event;

mod aardvarcv3;
mod aodsoc;
mod aodsv2;
mod asocv3;
mod asocv3s;
mod hdsocv1;
mod trbhmv1;
mod udc16;
mod upac96;
mod util;

pub type Sample = f32;
pub type WindowLabel = u16;
pub type TimeStamp = u16;
pub type Result<T, E = ParsingError> = std::result::Result<T, E>;

pub trait ParseInto<T: Event> {
    /// Try to parse the given raw event into an [`Event`] of the specified kind.
    ///
    /// # Errors
    /// - [`ParsingError::UnexpectedLength`] if the raw event length indicates the event cannot be parsed.
    /// - [`ParsingError::InvalidChannel`] if the event specifies a channel which is invalid for the acquisition parameters.
    /// - [`ParsingError::MissingData`] if the event is missing required data.
    /// - [`ParsingError::Other`] is a fallback for any unknown error.
    fn parse_into(&self, params: &Params) -> Result<T>;
    /// Perform a quick and dirty sanity check on the given raw event.
    ///
    /// The checks performed are different depending on the type of parser being used.
    /// However, if the check passes then the event is parseable in most cases.
    ///
    /// # Errors
    /// A subset of the errors specified in [`Parser::parse`] may be returned, depending
    /// on which parser is being used.
    fn fast_validate(&self, params: &Params) -> Result<()>;
}
