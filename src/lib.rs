use akatsuki_pp::{
    any::PerformanceAttributes,
    model::mode::GameMode,
    osu_2019::{stars::OsuPerformanceAttributes, OsuPP},
    Beatmap,
};
use interoptopus::{
    extra_type, ffi_function, ffi_type, function, patterns::option::FFIOption, Inventory,
    InventoryBuilder,
};
use std::ffi::CStr;
use std::os::raw::c_char;

#[ffi_type]
#[repr(C)]
#[derive(Clone, Default, PartialEq)]
pub struct CalculatePerformanceResult {
    pub pp: f64,
    pub stars: f64,
}

impl std::fmt::Display for CalculatePerformanceResult {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut s = f.debug_struct("CalculateResult");
        s.field("pp", &self.pp).field("stars", &self.stars);

        s.finish()
    }
}

impl CalculatePerformanceResult {
    fn from_attributes(attributes: PerformanceAttributes) -> Self {
        Self {
            pp: attributes.pp(),
            stars: attributes.stars(),
        }
    }

    fn from_rx_attributes(attributes: OsuPerformanceAttributes) -> Self {
        Self {
            pp: attributes.pp,
            stars: attributes.difficulty.stars,
        }
    }
}

#[ffi_function]
#[no_mangle]
pub unsafe extern "C" fn calculate_score(
    beatmap_path: *const c_char,
    mode: u32,
    mods: u32,
    max_combo: u32,
    accuracy: f64,
    miss_count: u32,
    passed_objects: FFIOption<u32>,
) -> CalculatePerformanceResult {
    let beatmap = Beatmap::from_path(CStr::from_ptr(beatmap_path).to_str().unwrap()).unwrap();

    // osu!std rx
    if mode == 0 && mods & 128 > 0 {
        let mut calculator = OsuPP::from_map(&beatmap);
        calculator = calculator.mods(mods).combo(max_combo).misses(miss_count);

        if let Some(passed_objects) = passed_objects.into_option() {
            calculator = calculator.passed_objects(passed_objects);
        }

        calculator = calculator.accuracy(accuracy as f32);

        let rosu_result = calculator.calculate();
        CalculatePerformanceResult::from_rx_attributes(rosu_result)
    } else {
        let mut calculator = beatmap
            .performance()
            .try_mode(match mode {
                0 => GameMode::Osu,
                1 => GameMode::Taiko,
                2 => GameMode::Catch,
                3 => GameMode::Mania,
                _ => panic!("Invalid mode"),
            })
            .unwrap()
            .mods(mods)
            .lazer(false)
            .combo(max_combo)
            .misses(miss_count);

        if let Some(passed_objects) = passed_objects.into_option() {
            calculator = calculator.passed_objects(passed_objects);
        }

        calculator = calculator.accuracy(accuracy);

        let rosu_result = calculator.calculate();
        CalculatePerformanceResult::from_attributes(rosu_result)
    }
}

pub fn my_inventory() -> Inventory {
    InventoryBuilder::new()
        .register(extra_type!(CalculatePerformanceResult))
        .register(function!(calculate_score))
        .inventory()
}
