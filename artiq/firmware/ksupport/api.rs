macro_rules! api {
    ($i:ident) => ({
        extern { static $i: u8; }
        api!($i = &$i as *const _)
    });
    ($i:ident, $d:item) => ({
        $d
        api!($i = $i)
    });
    ($i:ident = $e:expr) => {
        (stringify!($i), unsafe { $e as *const () })
    }
}

pub fn resolve(required: &str) -> usize {
    unsafe {
        API.iter()
           .find(|&&(exported, _)| exported == required)
           .map(|&(_, ptr)| ptr as usize)
           .unwrap_or(0)
    }
}

#[allow(unused_unsafe)]
static mut API: &'static [(&'static str, *const ())] = &[
    api!(__divsi3),
    api!(__modsi3),
    api!(__ledf2),
    api!(__gedf2),
    api!(__unorddf2),
    api!(__eqdf2),
    api!(__ltdf2),
    api!(__nedf2),
    api!(__gtdf2),
    api!(__negsf2),
    api!(__negdf2),
    api!(__addsf3),
    api!(__subsf3),
    api!(__mulsf3),
    api!(__divsf3),
    api!(__lshrdi3),
    api!(__muldi3),
    api!(__divdi3),
    api!(__ashldi3),
    api!(__ashrdi3),
    api!(__udivmoddi4),
    api!(__floatsisf),
    api!(__floatunsisf),
    api!(__fixsfsi),
    api!(__fixunssfsi),
    api!(__adddf3),
    api!(__subdf3),
    api!(__muldf3),
    api!(__divdf3),
    api!(__floatsidf),
    api!(__floatunsidf),
    api!(__floatdidf),
    api!(__fixdfsi),
    api!(__fixdfdi),
    api!(__fixunsdfsi),
    api!(__clzsi2),
    api!(__ctzsi2),
    api!(__udivdi3),
    api!(__umoddi3),
    api!(__moddi3),
    api!(__powidf2),

    /* libc */
    api!(abort = ::abort),
    api!(memcmp, extern { fn memcmp(a: *const u8, b: *mut u8, size: usize); }),

    /* libm */
    api!(sqrt),
    api!(round),

    /* exceptions */
    api!(_Unwind_Resume = ::unwind::_Unwind_Resume),
    api!(__artiq_personality = ::eh::personality),
    api!(__artiq_raise = ::eh::raise),
    api!(__artiq_reraise = ::eh::reraise),

    /* proxified syscalls */
    api!(core_log),

    api!(now = &::NOW as *const _),

    api!(watchdog_set = ::watchdog_set),
    api!(watchdog_clear = ::watchdog_clear),

    api!(send_rpc = ::send_rpc),
    api!(send_async_rpc = ::send_async_rpc),
    api!(recv_rpc = ::recv_rpc),

    api!(cache_get = ::cache_get),
    api!(cache_put = ::cache_put),

    /* direct syscalls */
    api!(rtio_init = ::rtio::init),
    api!(rtio_get_counter = ::rtio::get_counter),
    api!(rtio_log),
    api!(rtio_output = ::rtio::output),
    api!(rtio_output_wide = ::rtio::output_wide),
    api!(rtio_input_timestamp = ::rtio::input_timestamp),
    api!(rtio_input_data = ::rtio::input_data),

    api!(drtio_get_channel_state = ::rtio::drtio_dbg::get_channel_state),
    api!(drtio_reset_channel_state = ::rtio::drtio_dbg::reset_channel_state),
    api!(drtio_get_fifo_space = ::rtio::drtio_dbg::get_fifo_space),
    api!(drtio_get_packet_counts = ::rtio::drtio_dbg::get_packet_counts),
    api!(drtio_get_fifo_space_req_count = ::rtio::drtio_dbg::get_fifo_space_req_count),

    api!(i2c_start = ::i2c_start),
    api!(i2c_stop = ::i2c_stop),
    api!(i2c_write = ::i2c_write),
    api!(i2c_read = ::i2c_read),
];
