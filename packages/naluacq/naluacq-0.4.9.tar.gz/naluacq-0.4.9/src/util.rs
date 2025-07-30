/// Usage: `dispatch_by_event_type(model, err, fn_to_call, arg1, arg2, ...)`
///
/// This macro is used to invoke a `fn<T: impl Event>` with the correct event type based on the model.
macro_rules! dispatch_by_event_type {
    ($model:expr, $err:expr, $fn_to_call:ident, $($arg:expr),*) => {
        match $model {
            "aardvarcv3" => Ok($fn_to_call::<crate::Aardvarcv3Event>($($arg),*)),
            "aodsoc_aods" => Ok($fn_to_call::<crate::AodsocEvent>($($arg),*)),
            "aodsoc_asoc" => Ok($fn_to_call::<crate::AodsocEvent>($($arg),*)),
            "aodsv2" => Ok($fn_to_call::<crate::Aodsv2Event>($($arg),*)),
            "asocv3" => Ok($fn_to_call::<crate::Asocv3Event>($($arg),*)),
            "asocv3s" => Ok($fn_to_call::<crate::Asocv3SEvent>($($arg),*)),
            "hdsocv1_evalr2" => Ok($fn_to_call::<crate::Hdsocv1Event>($($arg),*)),
            "hdsocv2_eval" => Ok($fn_to_call::<crate::Hdsocv1Event>($($arg),*)),
            "hdsocv2_evalr1" => Ok($fn_to_call::<crate::Hdsocv1Event>($($arg),*)),
            "hdsocv2_evalr2" => Ok($fn_to_call::<crate::Hdsocv1Event>($($arg),*)),
            "trbhm" => Ok($fn_to_call::<crate::Trbhmv1Event>($($arg),*)),
            "udc16" => Ok($fn_to_call::<crate::Udc16Event>($($arg),*)),
            "upac96" => Ok($fn_to_call::<crate::Upac96Event>($($arg),*)),
            _ => Err($err),
        }
    };
}

pub(crate) use dispatch_by_event_type;
