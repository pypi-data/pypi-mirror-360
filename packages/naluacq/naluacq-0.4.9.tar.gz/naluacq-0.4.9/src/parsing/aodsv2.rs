use crate::{acquisition::Params, Event, ParseInto};

use super::{Asocv3Event, Result, Sample, TimeStamp, WindowLabel};

#[derive(Debug, Clone)]
pub struct Aodsv2Event {
    /// The data formats are the same for both AODSv2 and ASoCv3,
    /// so the ASoCv3 event type is reused.
    pub(crate) inner: Asocv3Event,
}

impl Aodsv2Event {
    pub fn new(channels: usize) -> Self {
        Self {
            inner: Asocv3Event::new(channels),
        }
    }

    pub fn prev_final_window(&self) -> WindowLabel {
        self.inner.prev_final_window()
    }

    pub fn trigger_time_ns(&self) -> u32 {
        self.inner.trigger_time_ns()
    }

    pub fn event_id(&self) -> u16 {
        self.inner.event_id()
    }
}

impl Event for Aodsv2Event {
    fn data(&self) -> &Vec<Vec<Sample>> {
        self.inner.data()
    }

    fn data_mut(&mut self) -> &mut Vec<Vec<Sample>> {
        self.inner.data_mut()
    }

    fn window_labels(&self) -> &Vec<Vec<WindowLabel>> {
        self.inner.window_labels()
    }

    fn time(&self) -> &Vec<Vec<TimeStamp>> {
        self.inner.time()
    }
}

impl ParseInto<Aodsv2Event> for [u8] {
    fn fast_validate(&self, params: &Params) -> Result<()> {
        <Self as ParseInto<Asocv3Event>>::fast_validate(&self, params)
    }

    fn parse_into(&self, params: &Params) -> Result<Aodsv2Event> {
        let mut event = Aodsv2Event::new(params.channels());
        event.inner = self.parse_into(params)?;
        Ok(event)
    }
}
