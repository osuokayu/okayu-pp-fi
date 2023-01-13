use akatsuki_pp::{
    osu_2019::{stars::OsuPerformanceAttributes, OsuPP},
    AnyPP, Beatmap, GameMode, PerformanceAttributes,
};
use interoptopus::{extra_type, ffi_function, ffi_type, function, Inventory, InventoryBuilder};
use std::ffi::CStr;
use std::os::raw::c_char;

#[ffi_type]
#[repr(C)]
#[derive(Clone, Default, PartialEq)]
pub struct CalculateResult {
    pub pp: f64,
    pub stars: f64,
}

impl std::fmt::Display for CalculateResult {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut s = f.debug_struct("CalculateResult");
        s.field("pp", &self.pp).field("stars", &self.stars);

        s.finish()
    }
}

impl CalculateResult {
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
) -> CalculateResult {
    let beatmap = Beatmap::from_path(CStr::from_ptr(beatmap_path).to_str().unwrap()).unwrap();

    // osu!std rx
    if mode == 0 && mods & 128 > 0 {
        let calculator = OsuPP::new(&beatmap);
        let rosu_result = calculator
            .mods(mods)
            .combo(max_combo as usize)
            .misses(miss_count as usize)
            .accuracy(accuracy as f32)
            .calculate();

        CalculateResult::from_rx_attributes(rosu_result)
    } else {
        let calculator = AnyPP::new(&beatmap);
        let rosu_result = calculator
            .mode(match mode {
                0 => GameMode::Osu,
                1 => GameMode::Taiko,
                2 => GameMode::Catch,
                3 => GameMode::Mania,
                _ => panic!("Invalid mode"),
            })
            .mods(mods)
            .combo(max_combo as usize)
            .n_misses(miss_count as usize)
            .accuracy(accuracy)
            .calculate();

        CalculateResult::from_attributes(rosu_result)
    }
}

pub fn my_inventory() -> Inventory {
    InventoryBuilder::new()
        .register(extra_type!(CalculateResult))
        .register(function!(calculate_score))
        .inventory()
}
