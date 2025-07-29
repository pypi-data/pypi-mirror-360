use std::error::Error;
use chrono::Duration;
use surrealdb::Response;

use crate::export;
use crate::db;


// pub async fn process_general_information_data(result: Response, select_type: u8)
// -> Result<Vec<(u64, String, String, String, String, String, String,String, u8, u16, u32, String, u32, String, u16, u16)>, Box<dyn Error>> {
//     let mut data = result;
//     let data: Vec<db::UdpTag40> = match data.take(0) {
//         Ok(data) => data,
//         Err(e) => {
//             println!("Error selecting general info data: {:?}", e);
//             return Err(Box::new(e));
//         }
//     };
    
//     if select_type == 1 {
//         return Ok(Vec::new());
//     }

//     let exploded_data: Vec<(u64, String, String, String, String, String, String,String, u8, u16, u32, String, u32, String, u16, u16)> = data
//         .into_iter()
//         .map(|tag| {
//             (
//                 tag.counter,
//                 tag.created,
//                 tag.firmware_revision,
//                 tag.firmware_version,
//                 format!("{}.{}.{}.{}", tag.ip_address[0], tag.ip_address[1], tag.ip_address[2], tag.ip_address[3]),
//                 format!("{}.{}.{}.{}", tag.ip_address_user_auto[0], tag.ip_address_user_auto[1], tag.ip_address_user_auto[2], tag.ip_address_user_auto[3]),
//                 tag.konfiguration,
//                 tag.mac_address,
//                 tag.number_of_channels,
//                 tag.port,
//                 tag.run_counter,
//                 tag.serial_number,
//                 format!("{}.{}.{}.{}", tag.subnet_mask[0], tag.subnet_mask[1], tag.subnet_mask[2], tag.subnet_mask[3]),
//                 tag.timestamp,
//                 tag.udp_port_sensor,
//                 tag.udp_port_user_auto
//             )
//         })
//         .collect();
//     Ok(exploded_data)
// }


pub async fn process_additonal_info_data(result: Response, ip_address: &str, name: &str, select_type: u8, number_of_channels:u8) 
-> Result<Vec<(u64, u16, u8, u16, u16, u16, u16, u16, u16, String)>, Box<dyn Error>> {
    let mut data = result;
    let data: Vec<db::UdpTag49> = match data.take(0) {
        Ok(data) => data,
        Err(e) => {
            println!("Error selecting additional info data: {:?}", e);
            return Err(Box::new(e));
        }
    };
    let ip = ip_address;
    
    match number_of_channels {
        1 => {
            export::store_additional_info_data_as_xlsx_1CH(&data, name, ip).await?;
        }
        2 => {
            export::store_additional_info_data_as_xlsx_2CH(&data, name, ip).await?;
        }
        3 => {
            export::store_additional_info_data_as_xlsx_3CH(&data, name, ip).await?;
        }
        4 => {
            export::store_additional_info_data_as_xlsx_4CH(&data, name, ip).await?;
        }
        5 => {
            export::store_additional_info_data_as_xlsx_5CH(&data, name, ip).await?;
        }
        6 => {
            export::store_additional_info_data_as_xlsx_6CH(&data, name, ip).await?;
        }
        7 => {
            export::store_additional_info_data_as_xlsx_7CH(&data, name, ip).await?;
        }
        8 => {
            export::store_additional_info_data_as_xlsx_8CH(&data, name, ip).await?;
        }
        9 => {
            export::store_additional_info_data_as_xlsx_9CH(&data, name, ip).await?;
        }
        10 => {
            export::store_additional_info_data_as_xlsx_10CH(&data, name, ip).await?;
        }
        11 => {
            export::store_additional_info_data_as_xlsx_11CH(&data, name, ip).await?;
        }
        12 => {
            export::store_additional_info_data_as_xlsx_12CH(&data, name, ip).await?;
        }
        _ => {
        }
    };
    if select_type == 1 {
        return Ok(Vec::new());
    }

    let exploded_data: Vec<(u64, u16, u8, u16, u16, u16, u16, u16, u16, String)> = data
        .into_iter()
        .flat_map(|tag| {
            tag.channel.into_iter()
                .zip(tag.peak.into_iter()) // Combine the channel and peak vectors
                .zip(tag.peak_position.into_iter())
                .zip(tag.position_over.into_iter())
                .zip(tag.position_under.into_iter())
                .zip(tag.offset_after.into_iter())
                .zip(tag.offset_before.into_iter())
                .map(move |((((((channel_value, peak_value), peak_position), position_over), position_under), offset_after), offset_before)| {
                    (tag.run_counter, tag.len_trigger, channel_value, peak_value, peak_position, position_over, position_under, offset_after, offset_before, tag.timestamp.clone())
                })
        })
        .collect();
    Ok(exploded_data)
}


pub async fn process_measurement_data(result: Response, ip_address: &str, name: &str, select_type:u8, number_of_channels:u8) 
-> Result<Vec<(u64, u8, u64, u64, u16, u16, u16, u16, u16, String, Vec<String>)>, Box<dyn Error>> {
    let mut data = result;
    let data: Vec<db::UdpTag41> = match data.take(0) {
        Ok(data) => data,
        Err(e) => {
            println!("Error selecting measurement data: {:?}", e);
            return Err(Box::new(e));
        }
    };
    let ip = ip_address;
    
    match number_of_channels {
        1 => {
            let _ = export::store_measurement_data_as_xlsx_1CH(&data, name, ip).await?;
        },
        2 => {
            let _ = export::store_measurement_data_as_xlsx_2CH(&data, name, ip).await?;
        },
        3 => {
            let _ = export::store_measurement_data_as_xlsx_3CH(&data, name, ip).await?;
        },
        4 => {
            let _ = export::store_measurement_data_as_xlsx_4CH(&data, name, ip).await?;
        },
        5 => {
            let _ = export::store_measurement_data_as_xlsx_5CH(&data, name, ip).await?;
        },
        6 => {
            let _ = export::store_measurement_data_as_xlsx_6CH(&data, name, ip).await?;
        },
        7 => {
            let _ = export::store_measurement_data_as_xlsx_7CH(&data, name, ip).await?;
        },
        8 => {
            let _ = export::store_measurement_data_as_xlsx_8CH(&data, name, ip).await?;
        },
        9 => {
            let _ = export::store_measurement_data_as_xlsx_9CH(&data, name, ip).await?;
        },
        10 => {
            let _ = export::store_measurement_data_as_xlsx_10CH(&data, name, ip).await?;
        },
        11 => {
            let _ = export::store_measurement_data_as_xlsx_11CH(&data, name, ip).await?;
        },
        12 => {
            let _ = export::store_measurement_data_as_xlsx_12CH(&data, name, ip).await?;
        },
        _ => {
        }
    }
    if select_type == 1 {
        return Ok(Vec::new());
    }
    
    let exploded_data: Vec<(u64, u8, u64, u64, u16, u16, u16, u16, u16, String, Vec<String>)> = data
        .into_iter()
        .flat_map(|tag| {
            tag.channel.into_iter()
                .zip(tag.integral.into_iter()) // Combine the channel and peak vectors
                .zip(tag.mass.into_iter())
                .zip(tag.offset.into_iter())
                .zip(tag.offset1.into_iter())
                .zip(tag.offset2.into_iter())
                .zip(tag.tolerance_bottom.into_iter())
                .zip(tag.tolerance_top.into_iter())
                .zip(tag.status.clone().into_iter())
                .map(move |((((((((channel_value, integral), mass), offset), offset1), offset2), tolerance_bottom), tolerance_top), status)| {
                    (tag.run_counter, channel_value, integral, mass, offset, offset1, offset2, tolerance_bottom, tolerance_top, tag.timestamp.clone(),status)
                })
        })
        .collect();
    Ok(exploded_data)
}


pub async fn process_raw_data(result: Response) -> Result<Vec<(u64, u8, i32, String, u32)>, Box<dyn Error>> {
    let mut ddata = result;
    let data: Vec<db::RawData> = match ddata.take(0) {
        Ok(data) => data,
        Err(e) => {
            println!("Error selecting raw data: {:?}", e);
            return Err(Box::new(e));
        }
    };
    let mut exploded_data = Vec::new();
        
    for tag in data {
            let channel_value = tag.channel;
            let run_counter = tag.run_counter;
            let timestamp = tag.timestamp;

            let mut i = 0;
            for data_value in tag.data {
                let duration: u32 = i as u32 * 250;
                let new_timestamp = timestamp + Duration::microseconds(i as i64 * 250);
                i += 1;
                exploded_data.push((run_counter, channel_value, data_value, new_timestamp.clone().to_string(), duration));
            }
        }
        
        Ok(exploded_data)
}