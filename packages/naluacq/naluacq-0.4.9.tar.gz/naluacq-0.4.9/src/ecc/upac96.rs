/// Calculate the syndrome for a given 16-bit data word.
/// The syndrome is a 4-byte array where each byte represents the parity of specific bits in the data word.
/// 
/// # Arguments
/// * `data` - A 16-bit unsigned integer representing the data word.
/// # Returns
/// * An array of 4 bytes, each representing the parity of specific bits in the data word.
///
pub fn syndrome(data: &u16) -> [u8; 4] {
    let mut s = [0u8; 4];
    let checks: [[u8; 7]; 4]  = [
        [0, 1, 3, 4, 6, 8, 10],
        [0, 2, 3, 5, 6, 9, 11],
        [1, 2, 3, 7, 8, 9, 12],
        [4, 5, 6, 7, 8, 9, 13],
    ];

    for (i, chk) in checks.iter().enumerate() {
        for &bit_idx in chk.iter() {
            s[i] ^= get_bit(data, bit_idx);
        }
    }
    s
}

/// Converts the syndrom array into the bitnumber.
/// 
/// The UDC chip doesn't add the ECC bits in the normal positions, but at the top.
/// 
/// # Arguments
/// * `s` - Syndrome array
/// # returns
/// * None or 
pub fn syndrome_to_index(s: &[u8; 4]) -> Option<u8> {
    // Map the syndrome to an index based on the corrections
    let corrections = [
        10, 11, 0, 12, 1, 2, 3, 13, 4, 5, 6, 7, 8, 9, 15,
    ];

    let index = ((s[3] as usize) << 3)
        + ((s[2] as usize) << 2)
        + ((s[1] as usize) << 1)
        + (s[0] as usize);

    if index == 0 || index > 16 {
        None
    } else {
        Some(corrections[index - 1])
    }
}

/// Calculate the global parity for a 16-bit data word.
/// 
/// The global parity is the XOR of all bits in the data word, excluding the last bit.
/// gp = d(0) xor  d(1) xor d(2) xor  d(3) xor  d(4) xor d(5) xor  d(6) xor d(7) xor  d(8) xor  d(9) xor d(10) xor d(11) xor d(12) xor d(13) xor d(14)
/// 
///# Arguments
/// * `data` - A 16-bit unsigned integer representing the data word.
/// # Returns
/// * An integer representing the global parity of the data word.
///
pub fn global_parity(data: &u16) -> u8 {
    (data.count_ones() as u8) & 1
}

/// Correct bits in a 16-bit data word based on the syndrome.
/// /// # Arguments
/// * `data` - A 16-bit unsigned integer representing the data word.
/// /// * `syndrome` - A 4-byte array representing the syndrome [s0, s1, s2, s3].
/// # Returns
/// * A 16-bit unsigned integer with the corrected data word.
pub fn correct_bit(data: &u16, index: u8) -> u16 {
    data ^ (1 << index)
}

/// Get the value of a specific bit in a 16-bit unsigned integer.
/// # Arguments
/// * `data` - A 16-bit unsigned integer.
/// * `bit` - The index of the bit to retrieve (0-15).
/// # Returns
/// * The value of the specified bit as a u8 (0 or 1).
fn get_bit(data: &u16, bit: u8) -> u8 {
    ((data >> bit) & 1) as u8
}
