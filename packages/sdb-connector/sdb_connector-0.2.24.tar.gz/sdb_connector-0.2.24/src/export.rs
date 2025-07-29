// ignore snake case
#![allow(non_snake_case)]

use std::error::Error;
use xlsxwriter::*;

use crate::db;

pub async fn error_matching(vec: &Vec<String>) -> Result<Vec<String>, Box<dyn Error>> {
    let mut status = vec.clone();
    for i in 0..status.len() {
        if status[i] == "00" {
            status[i] = "OK: Messwert im Toleranzbereich".to_string();
        } else if status[i] == "01" {
            "OK: Der Massewert überschreitet den Toleranzbereich".to_string();
        } else if status[i] == "02" {
            "OK: Der Massewert unterschreitet den Toleranzbereich".to_string();
        } else if status[i] == "03" {
            "FEHLER: Offsetabgleich Anschlag Stellgröße oben".to_string();
        } else if status[i] == "04" {
            "FEHLER: Offsetabgleich Anschlag Stellgröße unten".to_string();
        } else if status[i] == "05" {
            "FEHLER: Offsetabgleich war noch nicht fertig, als die Flanke des Offsettriggers kam".to_string();
        } else if status[i] == "06" {
            "FEHLER: Seit dem letzten Systemstart ist keine Messung vorhanden".to_string();
        } else if status[i] == "07" {
            "FEHLER: Der Offset befindet sich außerhalb des Messbereichs".to_string();
        } else if status[i] == "08" {
            "FEHLER: Der Messtrigger ist zu lang".to_string();
        } else if status[i] == "09" {
            "FEHLER: Der Messtrigger ist zu kurz".to_string();
        } else if status[i] == "10" {
            "FEHLER: Schräge Nulllinie: Schwellwert2 wurde nicht unterschritten".to_string();
        } else if status[i] == "11" {
            "FEHLER: Schräge Nulllinie: Zeit t1 liegt vor der steigenden Flanke des Messtriggers".to_string();
        } else if status[i] == "12" {
            "FEHLER: Schräge Nulllinie: Zeit t2 liegt nach der fallenden Flanke des Messtriggers".to_string();
        } else if status[i] == "13" {
            "FEHLER: Nulllinien Mittelung".to_string();
        } else if status[i] == "14" {
            "FEHLER: Nulllinien Berechnung".to_string();
        } else if status[i] == "15" {
            "FEHLER: maximal zulässige Anzahl von Umkehrpunkten wurde überschritten".to_string();
        } else if status[i] == "16" {
            "FEHLER: maximal zulässige Amplitude des Rauschens wurde überschritten".to_string();
        } else if status[i] == "17" {
            "FEHLER: Ein unzulässig hoher negativer Peak war vorhanden".to_string();
        } else if status[i] == "0A" {
            "FEHLER: Anschlag des Messsignals".to_string();
        } else if status[i] == "0B" {
            "FEHLER: Ein Variablenüberlauf bei der Masseberechnung ist aufgetreten".to_string();
        } else if status[i] == "0C" {
            "FEHLER: Überwachung des Messfensters - positiv".to_string();
        } else if status[i] == "0D" {
            "FEHLER: Überwachung des Messfensters - negativ".to_string();
        } else if status[i] == "0E" {
            "FEHLER: Bei dem Offsetabgleich ist ein Timeout aufgetreten".to_string();
        } else if status[i] == "0F" {
            "FEHLER: Schräge Nulllinie: Schwellwert1 wurde nicht überschritten".to_string();
        }
    }
    Ok(status)
}

pub async fn store_additional_info_data_as_xlsx_1CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;
        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_2CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;
    }
    Ok(())
}


pub async fn store_additional_info_data_as_xlsx_3CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_4CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_5CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
     "Offset Start CH4", "Offset Ende CH4", "Kurve Start CH4", "Kurve Ende CH4", "Peakwert CH4", "Peakposition CH4",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;

        worksheet.write_number(row, 29, entry.offset_before[4] as f64, None)?;
        worksheet.write_number(row, 30, entry.offset_after[4] as f64, None)?;
        worksheet.write_number(row, 31, entry.position_over[4] as f64, None)?;
        worksheet.write_number(row, 32, entry.position_under[4] as f64, None)?;
        worksheet.write_number(row, 33, entry.peak[4] as f64, None)?;
        worksheet.write_number(row, 34, entry.peak_position[4] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_6CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
     "Offset Start CH4", "Offset Ende CH4", "Kurve Start CH4", "Kurve Ende CH4", "Peakwert CH4", "Peakposition CH4",
     "Offset Start CH5", "Offset Ende CH5", "Kurve Start CH5", "Kurve Ende CH5", "Peakwert CH5", "Peakposition CH5",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;

        worksheet.write_number(row, 29, entry.offset_before[4] as f64, None)?;
        worksheet.write_number(row, 30, entry.offset_after[4] as f64, None)?;
        worksheet.write_number(row, 31, entry.position_over[4] as f64, None)?;
        worksheet.write_number(row, 32, entry.position_under[4] as f64, None)?;
        worksheet.write_number(row, 33, entry.peak[4] as f64, None)?;
        worksheet.write_number(row, 34, entry.peak_position[4] as f64, None)?;

        worksheet.write_number(row, 35, entry.offset_before[5] as f64, None)?;
        worksheet.write_number(row, 36, entry.offset_after[5] as f64, None)?;
        worksheet.write_number(row, 37, entry.position_over[5] as f64, None)?;
        worksheet.write_number(row, 38, entry.position_under[5] as f64, None)?;
        worksheet.write_number(row, 39, entry.peak[5] as f64, None)?;
        worksheet.write_number(row, 40, entry.peak_position[5] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_7CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
     "Offset Start CH4", "Offset Ende CH4", "Kurve Start CH4", "Kurve Ende CH4", "Peakwert CH4", "Peakposition CH4",
     "Offset Start CH5", "Offset Ende CH5", "Kurve Start CH5", "Kurve Ende CH5", "Peakwert CH5", "Peakposition CH5",
     "Offset Start CH6", "Offset Ende CH6", "Kurve Start CH6", "Kurve Ende CH6", "Peakwert CH6", "Peakposition CH6",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;

        worksheet.write_number(row, 29, entry.offset_before[4] as f64, None)?;
        worksheet.write_number(row, 30, entry.offset_after[4] as f64, None)?;
        worksheet.write_number(row, 31, entry.position_over[4] as f64, None)?;
        worksheet.write_number(row, 32, entry.position_under[4] as f64, None)?;
        worksheet.write_number(row, 33, entry.peak[4] as f64, None)?;
        worksheet.write_number(row, 34, entry.peak_position[4] as f64, None)?;

        worksheet.write_number(row, 35, entry.offset_before[5] as f64, None)?;
        worksheet.write_number(row, 36, entry.offset_after[5] as f64, None)?;
        worksheet.write_number(row, 37, entry.position_over[5] as f64, None)?;
        worksheet.write_number(row, 38, entry.position_under[5] as f64, None)?;
        worksheet.write_number(row, 39, entry.peak[5] as f64, None)?;
        worksheet.write_number(row, 40, entry.peak_position[5] as f64, None)?;

        worksheet.write_number(row, 41, entry.offset_before[6] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset_after[6] as f64, None)?;
        worksheet.write_number(row, 43, entry.position_over[6] as f64, None)?;
        worksheet.write_number(row, 44, entry.position_under[6] as f64, None)?;
        worksheet.write_number(row, 45, entry.peak[6] as f64, None)?;
        worksheet.write_number(row, 46, entry.peak_position[6] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_8CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
     "Offset Start CH4", "Offset Ende CH4", "Kurve Start CH4", "Kurve Ende CH4", "Peakwert CH4", "Peakposition CH4",
     "Offset Start CH5", "Offset Ende CH5", "Kurve Start CH5", "Kurve Ende CH5", "Peakwert CH5", "Peakposition CH5",
     "Offset Start CH6", "Offset Ende CH6", "Kurve Start CH6", "Kurve Ende CH6", "Peakwert CH6", "Peakposition CH6",
     "Offset Start CH7", "Offset Ende CH7", "Kurve Start CH7", "Kurve Ende CH7", "Peakwert CH7", "Peakposition CH7",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;

        worksheet.write_number(row, 29, entry.offset_before[4] as f64, None)?;
        worksheet.write_number(row, 30, entry.offset_after[4] as f64, None)?;
        worksheet.write_number(row, 31, entry.position_over[4] as f64, None)?;
        worksheet.write_number(row, 32, entry.position_under[4] as f64, None)?;
        worksheet.write_number(row, 33, entry.peak[4] as f64, None)?;
        worksheet.write_number(row, 34, entry.peak_position[4] as f64, None)?;

        worksheet.write_number(row, 35, entry.offset_before[5] as f64, None)?;
        worksheet.write_number(row, 36, entry.offset_after[5] as f64, None)?;
        worksheet.write_number(row, 37, entry.position_over[5] as f64, None)?;
        worksheet.write_number(row, 38, entry.position_under[5] as f64, None)?;
        worksheet.write_number(row, 39, entry.peak[5] as f64, None)?;
        worksheet.write_number(row, 40, entry.peak_position[5] as f64, None)?;

        worksheet.write_number(row, 41, entry.offset_before[6] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset_after[6] as f64, None)?;
        worksheet.write_number(row, 43, entry.position_over[6] as f64, None)?;
        worksheet.write_number(row, 44, entry.position_under[6] as f64, None)?;
        worksheet.write_number(row, 45, entry.peak[6] as f64, None)?;
        worksheet.write_number(row, 46, entry.peak_position[6] as f64, None)?;
        
        worksheet.write_number(row, 47, entry.offset_before[7] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset_after[7] as f64, None)?;
        worksheet.write_number(row, 49, entry.position_over[7] as f64, None)?;
        worksheet.write_number(row, 50, entry.position_under[7] as f64, None)?;
        worksheet.write_number(row, 51, entry.peak[7] as f64, None)?;
        worksheet.write_number(row, 52, entry.peak_position[7] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_9CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
     "Offset Start CH4", "Offset Ende CH4", "Kurve Start CH4", "Kurve Ende CH4", "Peakwert CH4", "Peakposition CH4",
     "Offset Start CH5", "Offset Ende CH5", "Kurve Start CH5", "Kurve Ende CH5", "Peakwert CH5", "Peakposition CH5",
     "Offset Start CH6", "Offset Ende CH6", "Kurve Start CH6", "Kurve Ende CH6", "Peakwert CH6", "Peakposition CH6",
     "Offset Start CH7", "Offset Ende CH7", "Kurve Start CH7", "Kurve Ende CH7", "Peakwert CH7", "Peakposition CH7",
    "Offset Start CH8", "Offset Ende CH8", "Kurve Start CH8", "Kurve Ende CH8", "Peakwert CH8", "Peakposition CH8",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;

        worksheet.write_number(row, 29, entry.offset_before[4] as f64, None)?;
        worksheet.write_number(row, 30, entry.offset_after[4] as f64, None)?;
        worksheet.write_number(row, 31, entry.position_over[4] as f64, None)?;
        worksheet.write_number(row, 32, entry.position_under[4] as f64, None)?;
        worksheet.write_number(row, 33, entry.peak[4] as f64, None)?;
        worksheet.write_number(row, 34, entry.peak_position[4] as f64, None)?;

        worksheet.write_number(row, 35, entry.offset_before[5] as f64, None)?;
        worksheet.write_number(row, 36, entry.offset_after[5] as f64, None)?;
        worksheet.write_number(row, 37, entry.position_over[5] as f64, None)?;
        worksheet.write_number(row, 38, entry.position_under[5] as f64, None)?;
        worksheet.write_number(row, 39, entry.peak[5] as f64, None)?;
        worksheet.write_number(row, 40, entry.peak_position[5] as f64, None)?;

        worksheet.write_number(row, 41, entry.offset_before[6] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset_after[6] as f64, None)?;
        worksheet.write_number(row, 43, entry.position_over[6] as f64, None)?;
        worksheet.write_number(row, 44, entry.position_under[6] as f64, None)?;
        worksheet.write_number(row, 45, entry.peak[6] as f64, None)?;
        worksheet.write_number(row, 46, entry.peak_position[6] as f64, None)?;
        
        worksheet.write_number(row, 47, entry.offset_before[7] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset_after[7] as f64, None)?;
        worksheet.write_number(row, 49, entry.position_over[7] as f64, None)?;
        worksheet.write_number(row, 50, entry.position_under[7] as f64, None)?;
        worksheet.write_number(row, 51, entry.peak[7] as f64, None)?;
        worksheet.write_number(row, 52, entry.peak_position[7] as f64, None)?;

        worksheet.write_number(row, 53, entry.offset_before[8] as f64, None)?;
        worksheet.write_number(row, 54, entry.offset_after[8] as f64, None)?;
        worksheet.write_number(row, 55, entry.position_over[8] as f64, None)?;
        worksheet.write_number(row, 56, entry.position_under[8] as f64, None)?;
        worksheet.write_number(row, 57, entry.peak[8] as f64, None)?;
        worksheet.write_number(row, 58, entry.peak_position[8] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_10CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
     "Offset Start CH4", "Offset Ende CH4", "Kurve Start CH4", "Kurve Ende CH4", "Peakwert CH4", "Peakposition CH4",
     "Offset Start CH5", "Offset Ende CH5", "Kurve Start CH5", "Kurve Ende CH5", "Peakwert CH5", "Peakposition CH5",
     "Offset Start CH6", "Offset Ende CH6", "Kurve Start CH6", "Kurve Ende CH6", "Peakwert CH6", "Peakposition CH6",
     "Offset Start CH7", "Offset Ende CH7", "Kurve Start CH7", "Kurve Ende CH7", "Peakwert CH7", "Peakposition CH7",
    "Offset Start CH8", "Offset Ende CH8", "Kurve Start CH8", "Kurve Ende CH8", "Peakwert CH8", "Peakposition CH8",
    "Offset Start CH9", "Offset Ende CH9", "Kurve Start CH9", "Kurve Ende CH9", "Peakwert CH9", "Peakposition CH9",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;

        worksheet.write_number(row, 29, entry.offset_before[4] as f64, None)?;
        worksheet.write_number(row, 30, entry.offset_after[4] as f64, None)?;
        worksheet.write_number(row, 31, entry.position_over[4] as f64, None)?;
        worksheet.write_number(row, 32, entry.position_under[4] as f64, None)?;
        worksheet.write_number(row, 33, entry.peak[4] as f64, None)?;
        worksheet.write_number(row, 34, entry.peak_position[4] as f64, None)?;

        worksheet.write_number(row, 35, entry.offset_before[5] as f64, None)?;
        worksheet.write_number(row, 36, entry.offset_after[5] as f64, None)?;
        worksheet.write_number(row, 37, entry.position_over[5] as f64, None)?;
        worksheet.write_number(row, 38, entry.position_under[5] as f64, None)?;
        worksheet.write_number(row, 39, entry.peak[5] as f64, None)?;
        worksheet.write_number(row, 40, entry.peak_position[5] as f64, None)?;

        worksheet.write_number(row, 41, entry.offset_before[6] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset_after[6] as f64, None)?;
        worksheet.write_number(row, 43, entry.position_over[6] as f64, None)?;
        worksheet.write_number(row, 44, entry.position_under[6] as f64, None)?;
        worksheet.write_number(row, 45, entry.peak[6] as f64, None)?;
        worksheet.write_number(row, 46, entry.peak_position[6] as f64, None)?;
        
        worksheet.write_number(row, 47, entry.offset_before[7] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset_after[7] as f64, None)?;
        worksheet.write_number(row, 49, entry.position_over[7] as f64, None)?;
        worksheet.write_number(row, 50, entry.position_under[7] as f64, None)?;
        worksheet.write_number(row, 51, entry.peak[7] as f64, None)?;
        worksheet.write_number(row, 52, entry.peak_position[7] as f64, None)?;

        worksheet.write_number(row, 53, entry.offset_before[8] as f64, None)?;
        worksheet.write_number(row, 54, entry.offset_after[8] as f64, None)?;
        worksheet.write_number(row, 55, entry.position_over[8] as f64, None)?;
        worksheet.write_number(row, 56, entry.position_under[8] as f64, None)?;
        worksheet.write_number(row, 57, entry.peak[8] as f64, None)?;
        worksheet.write_number(row, 58, entry.peak_position[8] as f64, None)?;

        worksheet.write_number(row, 59, entry.offset_before[9] as f64, None)?;
        worksheet.write_number(row, 60, entry.offset_after[9] as f64, None)?;
        worksheet.write_number(row, 61, entry.position_over[9] as f64, None)?;
        worksheet.write_number(row, 62, entry.position_under[9] as f64, None)?;
        worksheet.write_number(row, 63, entry.peak[9] as f64, None)?;
        worksheet.write_number(row, 64, entry.peak_position[9] as f64, None)?;
    }
    Ok(())
}

pub async fn store_additional_info_data_as_xlsx_11CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
     "Offset Start CH4", "Offset Ende CH4", "Kurve Start CH4", "Kurve Ende CH4", "Peakwert CH4", "Peakposition CH4",
     "Offset Start CH5", "Offset Ende CH5", "Kurve Start CH5", "Kurve Ende CH5", "Peakwert CH5", "Peakposition CH5",
     "Offset Start CH6", "Offset Ende CH6", "Kurve Start CH6", "Kurve Ende CH6", "Peakwert CH6", "Peakposition CH6",
     "Offset Start CH7", "Offset Ende CH7", "Kurve Start CH7", "Kurve Ende CH7", "Peakwert CH7", "Peakposition CH7",
    "Offset Start CH8", "Offset Ende CH8", "Kurve Start CH8", "Kurve Ende CH8", "Peakwert CH8", "Peakposition CH8",
    "Offset Start CH9", "Offset Ende CH9", "Kurve Start CH9", "Kurve Ende CH9", "Peakwert CH9", "Peakposition CH9",
    "Offset Start CH10", "Offset Ende CH10", "Kurve Start CH10", "Kurve Ende CH10", "Peakwert CH10", "Peakposition CH10",
    
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;

        worksheet.write_number(row, 29, entry.offset_before[4] as f64, None)?;
        worksheet.write_number(row, 30, entry.offset_after[4] as f64, None)?;
        worksheet.write_number(row, 31, entry.position_over[4] as f64, None)?;
        worksheet.write_number(row, 32, entry.position_under[4] as f64, None)?;
        worksheet.write_number(row, 33, entry.peak[4] as f64, None)?;
        worksheet.write_number(row, 34, entry.peak_position[4] as f64, None)?;

        worksheet.write_number(row, 35, entry.offset_before[5] as f64, None)?;
        worksheet.write_number(row, 36, entry.offset_after[5] as f64, None)?;
        worksheet.write_number(row, 37, entry.position_over[5] as f64, None)?;
        worksheet.write_number(row, 38, entry.position_under[5] as f64, None)?;
        worksheet.write_number(row, 39, entry.peak[5] as f64, None)?;
        worksheet.write_number(row, 40, entry.peak_position[5] as f64, None)?;

        worksheet.write_number(row, 41, entry.offset_before[6] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset_after[6] as f64, None)?;
        worksheet.write_number(row, 43, entry.position_over[6] as f64, None)?;
        worksheet.write_number(row, 44, entry.position_under[6] as f64, None)?;
        worksheet.write_number(row, 45, entry.peak[6] as f64, None)?;
        worksheet.write_number(row, 46, entry.peak_position[6] as f64, None)?;
        
        worksheet.write_number(row, 47, entry.offset_before[7] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset_after[7] as f64, None)?;
        worksheet.write_number(row, 49, entry.position_over[7] as f64, None)?;
        worksheet.write_number(row, 50, entry.position_under[7] as f64, None)?;
        worksheet.write_number(row, 51, entry.peak[7] as f64, None)?;
        worksheet.write_number(row, 52, entry.peak_position[7] as f64, None)?;

        worksheet.write_number(row, 53, entry.offset_before[8] as f64, None)?;
        worksheet.write_number(row, 54, entry.offset_after[8] as f64, None)?;
        worksheet.write_number(row, 55, entry.position_over[8] as f64, None)?;
        worksheet.write_number(row, 56, entry.position_under[8] as f64, None)?;
        worksheet.write_number(row, 57, entry.peak[8] as f64, None)?;
        worksheet.write_number(row, 58, entry.peak_position[8] as f64, None)?;

        worksheet.write_number(row, 59, entry.offset_before[9] as f64, None)?;
        worksheet.write_number(row, 60, entry.offset_after[9] as f64, None)?;
        worksheet.write_number(row, 61, entry.position_over[9] as f64, None)?;
        worksheet.write_number(row, 62, entry.position_under[9] as f64, None)?;
        worksheet.write_number(row, 63, entry.peak[9] as f64, None)?;
        worksheet.write_number(row, 64, entry.peak_position[9] as f64, None)?;

        worksheet.write_number(row, 65, entry.offset_before[10] as f64, None)?;
        worksheet.write_number(row, 66, entry.offset_after[10] as f64, None)?;
        worksheet.write_number(row, 67, entry.position_over[10] as f64, None)?;
        worksheet.write_number(row, 68, entry.position_under[10] as f64, None)?;
        worksheet.write_number(row, 69, entry.peak[10] as f64, None)?;
        worksheet.write_number(row, 70, entry.peak_position[10] as f64, None)?;
        
    }
    Ok(())
}


pub async fn store_additional_info_data_as_xlsx_12CH(data: &Vec<db::UdpTag49>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel Messung", "Highphase Messtrigger",
     "Offset Start CH0", "Offset Ende CH0", "Kurve Start CH0", "Kurve Ende CH0", "Peakwert CH0", "Peakposition CH0",
     "Offset Start CH1", "Offset Ende CH1", "Kurve Start CH1", "Kurve Ende CH1", "Peakwert CH1", "Peakposition CH1",
     "Offset Start CH2", "Offset Ende CH2", "Kurve Start CH2", "Kurve Ende CH2", "Peakwert CH2", "Peakposition CH2",
     "Offset Start CH3", "Offset Ende CH3", "Kurve Start CH3", "Kurve Ende CH3", "Peakwert CH3", "Peakposition CH3",
     "Offset Start CH4", "Offset Ende CH4", "Kurve Start CH4", "Kurve Ende CH4", "Peakwert CH4", "Peakposition CH4",
     "Offset Start CH5", "Offset Ende CH5", "Kurve Start CH5", "Kurve Ende CH5", "Peakwert CH5", "Peakposition CH5",
     "Offset Start CH6", "Offset Ende CH6", "Kurve Start CH6", "Kurve Ende CH6", "Peakwert CH6", "Peakposition CH6",
     "Offset Start CH7", "Offset Ende CH7", "Kurve Start CH7", "Kurve Ende CH7", "Peakwert CH7", "Peakposition CH7",
    "Offset Start CH8", "Offset Ende CH8", "Kurve Start CH8", "Kurve Ende CH8", "Peakwert CH8", "Peakposition CH8",
    "Offset Start CH9", "Offset Ende CH9", "Kurve Start CH9", "Kurve Ende CH9", "Peakwert CH9", "Peakposition CH9",
    "Offset Start CH10", "Offset Ende CH10", "Kurve Start CH10", "Kurve Ende CH10", "Peakwert CH10", "Peakposition CH10",
    "Offset Start CH11", "Offset Ende CH11", "Kurve Start CH11", "Kurve Ende CH11", "Peakwert CH11", "Peakposition CH11",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 3, &entry.timestamp, None)?;
        worksheet.write_number(row, 4, entry.len_trigger as f64, None)?;

        worksheet.write_number(row, 5, entry.offset_before[0] as f64, None)?;
        worksheet.write_number(row, 6, entry.offset_after[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.position_over[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.position_under[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.peak[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.peak_position[0] as f64, None)?;

        worksheet.write_number(row, 11, entry.offset_before[1] as f64, None)?;
        worksheet.write_number(row, 12, entry.offset_after[1] as f64, None)?;
        worksheet.write_number(row, 13, entry.position_over[1] as f64, None)?;
        worksheet.write_number(row, 14, entry.position_under[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.peak[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.peak_position[1] as f64, None)?;


        worksheet.write_number(row, 17, entry.offset_before[2] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset_after[2] as f64, None)?;
        worksheet.write_number(row, 19, entry.position_over[2] as f64, None)?;
        worksheet.write_number(row, 20, entry.position_under[2] as f64, None)?;
        worksheet.write_number(row, 21, entry.peak[2] as f64, None)?;
        worksheet.write_number(row, 22, entry.peak_position[2] as f64, None)?;

        worksheet.write_number(row, 23, entry.offset_before[3] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset_after[3] as f64, None)?;
        worksheet.write_number(row, 25, entry.position_over[3] as f64, None)?;
        worksheet.write_number(row, 26, entry.position_under[3] as f64, None)?;
        worksheet.write_number(row, 27, entry.peak[3] as f64, None)?;
        worksheet.write_number(row, 28, entry.peak_position[3] as f64, None)?;

        worksheet.write_number(row, 29, entry.offset_before[4] as f64, None)?;
        worksheet.write_number(row, 30, entry.offset_after[4] as f64, None)?;
        worksheet.write_number(row, 31, entry.position_over[4] as f64, None)?;
        worksheet.write_number(row, 32, entry.position_under[4] as f64, None)?;
        worksheet.write_number(row, 33, entry.peak[4] as f64, None)?;
        worksheet.write_number(row, 34, entry.peak_position[4] as f64, None)?;

        worksheet.write_number(row, 35, entry.offset_before[5] as f64, None)?;
        worksheet.write_number(row, 36, entry.offset_after[5] as f64, None)?;
        worksheet.write_number(row, 37, entry.position_over[5] as f64, None)?;
        worksheet.write_number(row, 38, entry.position_under[5] as f64, None)?;
        worksheet.write_number(row, 39, entry.peak[5] as f64, None)?;
        worksheet.write_number(row, 40, entry.peak_position[5] as f64, None)?;

        worksheet.write_number(row, 41, entry.offset_before[6] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset_after[6] as f64, None)?;
        worksheet.write_number(row, 43, entry.position_over[6] as f64, None)?;
        worksheet.write_number(row, 44, entry.position_under[6] as f64, None)?;
        worksheet.write_number(row, 45, entry.peak[6] as f64, None)?;
        worksheet.write_number(row, 46, entry.peak_position[6] as f64, None)?;
        
        worksheet.write_number(row, 47, entry.offset_before[7] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset_after[7] as f64, None)?;
        worksheet.write_number(row, 49, entry.position_over[7] as f64, None)?;
        worksheet.write_number(row, 50, entry.position_under[7] as f64, None)?;
        worksheet.write_number(row, 51, entry.peak[7] as f64, None)?;
        worksheet.write_number(row, 52, entry.peak_position[7] as f64, None)?;

        worksheet.write_number(row, 53, entry.offset_before[8] as f64, None)?;
        worksheet.write_number(row, 54, entry.offset_after[8] as f64, None)?;
        worksheet.write_number(row, 55, entry.position_over[8] as f64, None)?;
        worksheet.write_number(row, 56, entry.position_under[8] as f64, None)?;
        worksheet.write_number(row, 57, entry.peak[8] as f64, None)?;
        worksheet.write_number(row, 58, entry.peak_position[8] as f64, None)?;

        worksheet.write_number(row, 59, entry.offset_before[9] as f64, None)?;
        worksheet.write_number(row, 60, entry.offset_after[9] as f64, None)?;
        worksheet.write_number(row, 61, entry.position_over[9] as f64, None)?;
        worksheet.write_number(row, 62, entry.position_under[9] as f64, None)?;
        worksheet.write_number(row, 63, entry.peak[9] as f64, None)?;
        worksheet.write_number(row, 64, entry.peak_position[9] as f64, None)?;

        worksheet.write_number(row, 65, entry.offset_before[10] as f64, None)?;
        worksheet.write_number(row, 66, entry.offset_after[10] as f64, None)?;
        worksheet.write_number(row, 67, entry.position_over[10] as f64, None)?;
        worksheet.write_number(row, 68, entry.position_under[10] as f64, None)?;
        worksheet.write_number(row, 69, entry.peak[10] as f64, None)?;
        worksheet.write_number(row, 70, entry.peak_position[10] as f64, None)?;

        worksheet.write_number(row, 71, entry.offset_before[11] as f64, None)?;
        worksheet.write_number(row, 72, entry.offset_after[11] as f64, None)?;
        worksheet.write_number(row, 73, entry.position_over[11] as f64, None)?;
        worksheet.write_number(row, 74, entry.position_under[11] as f64, None)?;
        worksheet.write_number(row, 75, entry.peak[11] as f64, None)?;
        worksheet.write_number(row, 76, entry.peak_position[11] as f64, None)?;

    }
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_1CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
    ];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;
    }
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_2CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip = "172.30.1.122";

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1"];
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }
    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;


        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;
    }
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_3CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip = "172.30.1.122";
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;
    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;

        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

    }
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_4CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip = "172.30.1.122";

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;

        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;
        let status = error_matching(&entry.status[3]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;
    }

    Ok(())
}


pub async fn store_measurement_data_as_xlsx_5CH(data: &Vec<db::UdpTag41>, name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3",
     "Integral_CH4", "Masse_CH4", "Offsetwert_CH4", "Offsetwert1_CH4", "Offsetwert2_CH4", "Grenze_Masse_unten_CH4", "Grenze_Masse_oben_CH4", "Status_der_Messung_CH4"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;

        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;
        let status = error_matching(&entry.status[3]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;

        worksheet.write_number(row, 38, entry.integral[4] as f64, None)?;
        worksheet.write_number(row, 39, entry.mass[4] as f64, None)?;
        worksheet.write_number(row, 40, entry.offset[4] as f64, None)?;
        worksheet.write_number(row, 41, entry.offset1[4] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset2[4] as f64, None)?;
        worksheet.write_number(row, 43, entry.tolerance_bottom[4] as f64, None)?;
        worksheet.write_number(row, 44, entry.tolerance_top[4] as f64, None)?;
        let status = error_matching(&entry.status[4]).await?;
        worksheet.write_string(row, 45, &status.join(","), None)?;
    }

    Ok(())
}

pub async fn store_measurement_data_as_xlsx_6CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip = "172.30.1.122";

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3",
     "Integral_CH4", "Masse_CH4", "Offsetwert_CH4", "Offsetwert1_CH4", "Offsetwert2_CH4", "Grenze_Masse_unten_CH4", "Grenze_Masse_oben_CH4", "Status_der_Messung_CH4",
     "Integral_CH5", "Masse_CH5", "Offsetwert_CH5", "Offsetwert1_CH5", "Offsetwert2_CH5", "Grenze_Masse_unten_CH5", "Grenze_Masse_oben_CH5", "Status_der_Messung_CH5"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;

        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;

        worksheet.write_number(row, 38, entry.integral[4] as f64, None)?;
        worksheet.write_number(row, 39, entry.mass[4] as f64, None)?;
        worksheet.write_number(row, 40, entry.offset[4] as f64, None)?;
        worksheet.write_number(row, 41, entry.offset1[4] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset2[4] as f64, None)?;
        worksheet.write_number(row, 43, entry.tolerance_bottom[4] as f64, None)?;
        worksheet.write_number(row, 44, entry.tolerance_top[4] as f64, None)?;
        let status = error_matching(&entry.status[4]).await?;
        worksheet.write_string(row, 45, &status.join(","), None)?;

        worksheet.write_number(row, 46, entry.integral[5] as f64, None)?;
        worksheet.write_number(row, 47, entry.mass[5] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset[5] as f64, None)?;
        worksheet.write_number(row, 49, entry.offset1[5] as f64, None)?;
        worksheet.write_number(row, 50, entry.offset2[5] as f64, None)?;
        worksheet.write_number(row, 51, entry.tolerance_bottom[5] as f64, None)?;
        worksheet.write_number(row, 52, entry.tolerance_top[5] as f64, None)?;
        let status = error_matching(&entry.status[5]).await?;
        worksheet.write_string(row, 53, &status.join(","), None)?;
    }
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_7CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip = "172.30.1.122";

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3",
     "Integral_CH4", "Masse_CH4", "Offsetwert_CH4", "Offsetwert1_CH4", "Offsetwert2_CH4", "Grenze_Masse_unten_CH4", "Grenze_Masse_oben_CH4", "Status_der_Messung_CH4",
     "Integral_CH5", "Masse_CH5", "Offsetwert_CH5", "Offsetwert1_CH5", "Offsetwert2_CH5", "Grenze_Masse_unten_CH5", "Grenze_Masse_oben_CH5", "Status_der_Messung_CH5",
     "Integral_CH6", "Masse_CH6", "Offsetwert_CH6", "Offsetwert1_CH6", "Offsetwert2_CH6", "Grenze_Masse_unten_CH6", "Grenze_Masse_oben_CH6", "Status_der_Messung_CH6"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        worksheet.write_string(row, 13, &entry.status[0][0], None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        worksheet.write_string(row, 21, &entry.status[1][0], None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 22, &status.join(","), None)?;

        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;
        worksheet.write_string(row, 37, &entry.status[3][0], None)?;
        let status = error_matching(&entry.status[3]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;

        worksheet.write_number(row, 38, entry.integral[4] as f64, None)?;
        worksheet.write_number(row, 39, entry.mass[4] as f64, None)?;
        worksheet.write_number(row, 40, entry.offset[4] as f64, None)?;
        worksheet.write_number(row, 41, entry.offset1[4] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset2[4] as f64, None)?;
        worksheet.write_number(row, 43, entry.tolerance_bottom[4] as f64, None)?;
        worksheet.write_number(row, 44, entry.tolerance_top[4] as f64, None)?;
        let status = error_matching(&entry.status[4]).await?;
        worksheet.write_string(row, 45, &status.join(","), None)?;

        worksheet.write_number(row, 46, entry.integral[5] as f64, None)?;
        worksheet.write_number(row, 47, entry.mass[5] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset[5] as f64, None)?;
        worksheet.write_number(row, 49, entry.offset1[5] as f64, None)?;
        worksheet.write_number(row, 50, entry.offset2[5] as f64, None)?;
        worksheet.write_number(row, 51, entry.tolerance_bottom[5] as f64, None)?;
        worksheet.write_number(row, 52, entry.tolerance_top[5] as f64, None)?;
        let status = error_matching(&entry.status[5]).await?;
        worksheet.write_string(row, 53, &status.join(","), None)?;

        worksheet.write_number(row, 54, entry.integral[6] as f64, None)?;
        worksheet.write_number(row, 55, entry.mass[6] as f64, None)?;
        worksheet.write_number(row, 56, entry.offset[6] as f64, None)?;
        worksheet.write_number(row, 57, entry.offset1[6] as f64, None)?;
        worksheet.write_number(row, 58, entry.offset2[6] as f64, None)?;
        worksheet.write_number(row, 59, entry.tolerance_bottom[6] as f64, None)?;
        worksheet.write_number(row, 60, entry.tolerance_top[6] as f64, None)?;
        let status = error_matching(&entry.status[6]).await?;
        worksheet.write_string(row, 61, &status.join(","), None)?;

    }
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_8CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip = "172.30.1.122";

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3",
     "Integral_CH4", "Masse_CH4", "Offsetwert_CH4", "Offsetwert1_CH4", "Offsetwert2_CH4", "Grenze_Masse_unten_CH4", "Grenze_Masse_oben_CH4", "Status_der_Messung_CH4",
     "Integral_CH5", "Masse_CH5", "Offsetwert_CH5", "Offsetwert1_CH5", "Offsetwert2_CH5", "Grenze_Masse_unten_CH5", "Grenze_Masse_oben_CH5", "Status_der_Messung_CH5",
     "Integral_CH6", "Masse_CH6", "Offsetwert_CH6", "Offsetwert1_CH6", "Offsetwert2_CH6", "Grenze_Masse_unten_CH6", "Grenze_Masse_oben_CH6", "Status_der_Messung_CH6",
     "Integral_CH7", "Masse_CH7", "Offsetwert_CH7", "Offsetwert1_CH7", "Offsetwert2_CH7", "Grenze_Masse_unten_CH7", "Grenze_Masse_oben_CH7", "Status_der_Messung_CH7"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;


        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;
        let status = error_matching(&entry.status[3]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;

        worksheet.write_number(row, 38, entry.integral[4] as f64, None)?;
        worksheet.write_number(row, 39, entry.mass[4] as f64, None)?;
        worksheet.write_number(row, 40, entry.offset[4] as f64, None)?;
        worksheet.write_number(row, 41, entry.offset1[4] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset2[4] as f64, None)?;
        worksheet.write_number(row, 43, entry.tolerance_bottom[4] as f64, None)?;
        worksheet.write_number(row, 44, entry.tolerance_top[4] as f64, None)?;
        let status = error_matching(&entry.status[4]).await?;
        worksheet.write_string(row, 45, &status.join(","), None)?;


        worksheet.write_number(row, 46, entry.integral[5] as f64, None)?;
        worksheet.write_number(row, 47, entry.mass[5] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset[5] as f64, None)?;
        worksheet.write_number(row, 49, entry.offset1[5] as f64, None)?;
        worksheet.write_number(row, 50, entry.offset2[5] as f64, None)?;
        worksheet.write_number(row, 51, entry.tolerance_bottom[5] as f64, None)?;
        worksheet.write_number(row, 52, entry.tolerance_top[5] as f64, None)?;
        let status = error_matching(&entry.status[5]).await?;
        worksheet.write_string(row, 53, &status.join(","), None)?;

        worksheet.write_number(row, 54, entry.integral[6] as f64, None)?;
        worksheet.write_number(row, 55, entry.mass[6] as f64, None)?;
        worksheet.write_number(row, 56, entry.offset[6] as f64, None)?;
        worksheet.write_number(row, 57, entry.offset1[6] as f64, None)?;
        worksheet.write_number(row, 58, entry.offset2[6] as f64, None)?;
        worksheet.write_number(row, 59, entry.tolerance_bottom[6] as f64, None)?;
        worksheet.write_number(row, 60, entry.tolerance_top[6] as f64, None)?;
        let status = error_matching(&entry.status[6]).await?;
        worksheet.write_string(row, 61, &status.join(","), None)?;

        worksheet.write_number(row, 62, entry.integral[7] as f64, None)?;
        worksheet.write_number(row, 63, entry.mass[7] as f64, None)?;
        worksheet.write_number(row, 64, entry.offset[7] as f64, None)?;
        worksheet.write_number(row, 65, entry.offset1[7] as f64, None)?;
        worksheet.write_number(row, 66, entry.offset2[7] as f64, None)?;
        worksheet.write_number(row, 67, entry.tolerance_bottom[7] as f64, None)?;
        worksheet.write_number(row, 68, entry.tolerance_top[7] as f64, None)?;
        let status = error_matching(&entry.status[7]).await?;
        worksheet.write_string(row, 69, &status.join(","), None)?;
    }
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_9CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip = "172.30.1.122";

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3",
     "Integral_CH4", "Masse_CH4", "Offsetwert_CH4", "Offsetwert1_CH4", "Offsetwert2_CH4", "Grenze_Masse_unten_CH4", "Grenze_Masse_oben_CH4", "Status_der_Messung_CH4",
     "Integral_CH5", "Masse_CH5", "Offsetwert_CH5", "Offsetwert1_CH5", "Offsetwert2_CH5", "Grenze_Masse_unten_CH5", "Grenze_Masse_oben_CH5", "Status_der_Messung_CH5",
     "Integral_CH6", "Masse_CH6", "Offsetwert_CH6", "Offsetwert1_CH6", "Offsetwert2_CH6", "Grenze_Masse_unten_CH6", "Grenze_Masse_oben_CH6", "Status_der_Messung_CH6",
     "Integral_CH7", "Masse_CH7", "Offsetwert_CH7", "Offsetwert1_CH7", "Offsetwert2_CH7", "Grenze_Masse_unten_CH7", "Grenze_Masse_oben_CH7", "Status_der_Messung_CH7",
     "Integral_CH8", "Masse_CH8", "Offsetwert_CH8", "Offsetwert1_CH8", "Offsetwert2_CH8", "Grenze_Masse_unten_CH8", "Grenze_Masse_oben_CH8", "Status_der_Messung_CH8"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        worksheet.write_string(row, 13, &entry.status[0][0], None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;

        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;

        let status = error_matching(&entry.status[3]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;

        worksheet.write_number(row, 38, entry.integral[4] as f64, None)?;
        worksheet.write_number(row, 39, entry.mass[4] as f64, None)?;
        worksheet.write_number(row, 40, entry.offset[4] as f64, None)?;
        worksheet.write_number(row, 41, entry.offset1[4] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset2[4] as f64, None)?;
        worksheet.write_number(row, 43, entry.tolerance_bottom[4] as f64, None)?;
        worksheet.write_number(row, 44, entry.tolerance_top[4] as f64, None)?;
        let status = error_matching(&entry.status[4]).await?;
        worksheet.write_string(row, 45, &status.join(","), None)?;

        worksheet.write_number(row, 46, entry.integral[5] as f64, None)?;
        worksheet.write_number(row, 47, entry.mass[5] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset[5] as f64, None)?;
        worksheet.write_number(row, 49, entry.offset1[5] as f64, None)?;
        worksheet.write_number(row, 50, entry.offset2[5] as f64, None)?;
        worksheet.write_number(row, 51, entry.tolerance_bottom[5] as f64, None)?;
        worksheet.write_number(row, 52, entry.tolerance_top[5] as f64, None)?;
        let status = error_matching(&entry.status[5]).await?;
        worksheet.write_string(row, 53, &status.join(","), None)?;

        worksheet.write_number(row, 54, entry.integral[6] as f64, None)?;
        worksheet.write_number(row, 55, entry.mass[6] as f64, None)?;
        worksheet.write_number(row, 56, entry.offset[6] as f64, None)?;
        worksheet.write_number(row, 57, entry.offset1[6] as f64, None)?;
        worksheet.write_number(row, 58, entry.offset2[6] as f64, None)?;
        worksheet.write_number(row, 59, entry.tolerance_bottom[6] as f64, None)?;
        worksheet.write_number(row, 60, entry.tolerance_top[6] as f64, None)?;
        let status = error_matching(&entry.status[6]).await?;
        worksheet.write_string(row, 61, &status.join(","), None)?;

        worksheet.write_number(row, 62, entry.integral[7] as f64, None)?;
        worksheet.write_number(row, 63, entry.mass[7] as f64, None)?;
        worksheet.write_number(row, 64, entry.offset[7] as f64, None)?;
        worksheet.write_number(row, 65, entry.offset1[7] as f64, None)?;
        worksheet.write_number(row, 66, entry.offset2[7] as f64, None)?;
        worksheet.write_number(row, 67, entry.tolerance_bottom[7] as f64, None)?;
        worksheet.write_number(row, 68, entry.tolerance_top[7] as f64, None)?;
        let status = error_matching(&entry.status[7]).await?;
        worksheet.write_string(row, 69, &status.join(","), None)?;

        worksheet.write_number(row, 70, entry.integral[8] as f64, None)?;
        worksheet.write_number(row, 71, entry.mass[8] as f64, None)?;
        worksheet.write_number(row, 72, entry.offset[8] as f64, None)?;
        worksheet.write_number(row, 73, entry.offset1[8] as f64, None)?;
        worksheet.write_number(row, 74, entry.offset2[8] as f64, None)?;
        worksheet.write_number(row, 75, entry.tolerance_bottom[8] as f64, None)?;
        worksheet.write_number(row, 76, entry.tolerance_top[8] as f64, None)?;
        let status = error_matching(&entry.status[8]).await?;
        worksheet.write_string(row, 77, &status.join(","), None)?;
    };
    
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_10CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip: &str = "172.30.1.122";

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3",
     "Integral_CH4", "Masse_CH4", "Offsetwert_CH4", "Offsetwert1_CH4", "Offsetwert2_CH4", "Grenze_Masse_unten_CH4", "Grenze_Masse_oben_CH4", "Status_der_Messung_CH4",
     "Integral_CH5", "Masse_CH5", "Offsetwert_CH5", "Offsetwert1_CH5", "Offsetwert2_CH5", "Grenze_Masse_unten_CH5", "Grenze_Masse_oben_CH5", "Status_der_Messung_CH5",
     "Integral_CH6", "Masse_CH6", "Offsetwert_CH6", "Offsetwert1_CH6", "Offsetwert2_CH6", "Grenze_Masse_unten_CH6", "Grenze_Masse_oben_CH6", "Status_der_Messung_CH6",
     "Integral_CH7", "Masse_CH7", "Offsetwert_CH7", "Offsetwert1_CH7", "Offsetwert2_CH7", "Grenze_Masse_unten_CH7", "Grenze_Masse_oben_CH7", "Status_der_Messung_CH7",
     "Integral_CH8", "Masse_CH8", "Offsetwert_CH8", "Offsetwert1_CH8", "Offsetwert2_CH8", "Grenze_Masse_unten_CH8", "Grenze_Masse_oben_CH8", "Status_der_Messung_CH8",
     "Integral_CH9", "Masse_CH9", "Offsetwert_CH9", "Offsetwert1_CH9", "Offsetwert2_CH9", "Grenze_Masse_unten_CH9", "Grenze_Masse_oben_CH9", "Status_der_Messung_CH9"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;


        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;
        let status = error_matching(&entry.status[3]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;

        worksheet.write_number(row, 38, entry.integral[4] as f64, None)?;
        worksheet.write_number(row, 39, entry.mass[4] as f64, None)?;
        worksheet.write_number(row, 40, entry.offset[4] as f64, None)?;
        worksheet.write_number(row, 41, entry.offset1[4] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset2[4] as f64, None)?;
        worksheet.write_number(row, 43, entry.tolerance_bottom[4] as f64, None)?;
        worksheet.write_number(row, 44, entry.tolerance_top[4] as f64, None)?;
        let status = error_matching(&entry.status[4]).await?;
        worksheet.write_string(row, 45, &status.join(","), None)?;

        worksheet.write_number(row, 46, entry.integral[5] as f64, None)?;
        worksheet.write_number(row, 47, entry.mass[5] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset[5] as f64, None)?;
        worksheet.write_number(row, 49, entry.offset1[5] as f64, None)?;
        worksheet.write_number(row, 50, entry.offset2[5] as f64, None)?;
        worksheet.write_number(row, 51, entry.tolerance_bottom[5] as f64, None)?;
        worksheet.write_number(row, 52, entry.tolerance_top[5] as f64, None)?;
        let status = error_matching(&entry.status[5]).await?;
        worksheet.write_string(row, 53, &status.join(","), None)?;

        worksheet.write_number(row, 54, entry.integral[6] as f64, None)?;
        worksheet.write_number(row, 55, entry.mass[6] as f64, None)?;
        worksheet.write_number(row, 56, entry.offset[6] as f64, None)?;
        worksheet.write_number(row, 57, entry.offset1[6] as f64, None)?;
        worksheet.write_number(row, 58, entry.offset2[6] as f64, None)?;
        worksheet.write_number(row, 59, entry.tolerance_bottom[6] as f64, None)?;
        worksheet.write_number(row, 60, entry.tolerance_top[6] as f64, None)?;
        let status = error_matching(&entry.status[6]).await?;
        worksheet.write_string(row, 61, &status.join(","), None)?;

        worksheet.write_number(row, 62, entry.integral[7] as f64, None)?;
        worksheet.write_number(row, 63, entry.mass[7] as f64, None)?;
        worksheet.write_number(row, 64, entry.offset[7] as f64, None)?;
        worksheet.write_number(row, 65, entry.offset1[7] as f64, None)?;
        worksheet.write_number(row, 66, entry.offset2[7] as f64, None)?;
        worksheet.write_number(row, 67, entry.tolerance_bottom[7] as f64, None)?;
        worksheet.write_number(row, 68, entry.tolerance_top[7] as f64, None)?;
        let status = error_matching(&entry.status[7]).await?;
        worksheet.write_string(row, 69, &status.join(","), None)?;

        worksheet.write_number(row, 70, entry.integral[8] as f64, None)?;
        worksheet.write_number(row, 71, entry.mass[8] as f64, None)?;
        worksheet.write_number(row, 72, entry.offset[8] as f64, None)?;
        worksheet.write_number(row, 73, entry.offset1[8] as f64, None)?;
        worksheet.write_number(row, 74, entry.offset2[8] as f64, None)?;
        worksheet.write_number(row, 75, entry.tolerance_bottom[8] as f64, None)?;
        worksheet.write_number(row, 76, entry.tolerance_top[8] as f64, None)?;
        let status = error_matching(&entry.status[8]).await?;
        worksheet.write_string(row, 77, &status.join(","), None)?;


        worksheet.write_number(row, 78, entry.integral[9] as f64, None)?;
        worksheet.write_number(row, 79, entry.mass[9] as f64, None)?;
        worksheet.write_number(row, 80, entry.offset[9] as f64, None)?;
        worksheet.write_number(row, 81, entry.offset1[9] as f64, None)?;
        worksheet.write_number(row, 82, entry.offset2[9] as f64, None)?;
        worksheet.write_number(row, 83, entry.tolerance_bottom[9] as f64, None)?;
        worksheet.write_number(row, 84, entry.tolerance_top[9] as f64, None)?;
        let status = error_matching(&entry.status[9]).await?;
        worksheet.write_string(row, 85, &status.join(","), None)?;
    }
    
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_11CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    //let ip = "172.30.1.122";

    // Write headers
    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3",
     "Integral_CH4", "Masse_CH4", "Offsetwert_CH4", "Offsetwert1_CH4", "Offsetwert2_CH4", "Grenze_Masse_unten_CH4", "Grenze_Masse_oben_CH4", "Status_der_Messung_CH4",
     "Integral_CH5", "Masse_CH5", "Offsetwert_CH5", "Offsetwert1_CH5", "Offsetwert2_CH5", "Grenze_Masse_unten_CH5", "Grenze_Masse_oben_CH5", "Status_der_Messung_CH5",
     "Integral_CH6", "Masse_CH6", "Offsetwert_CH6", "Offsetwert1_CH6", "Offsetwert2_CH6", "Grenze_Masse_unten_CH6", "Grenze_Masse_oben_CH6", "Status_der_Messung_CH6",
     "Integral_CH7", "Masse_CH7", "Offsetwert_CH7", "Offsetwert1_CH7", "Offsetwert2_CH7", "Grenze_Masse_unten_CH7", "Grenze_Masse_oben_CH7", "Status_der_Messung_CH7",
     "Integral_CH8", "Masse_CH8", "Offsetwert_CH8", "Offsetwert1_CH8", "Offsetwert2_CH8", "Grenze_Masse_unten_CH8", "Grenze_Masse_oben_CH8", "Status_der_Messung_CH8",
     "Integral_CH9", "Masse_CH9", "Offsetwert_CH9", "Offsetwert1_CH9", "Offsetwert2_CH9", "Grenze_Masse_unten_CH9", "Grenze_Masse_oben_CH9", "Status_der_Messung_CH9",
     "Integral_CH10", "Masse_CH10", "Offsetwert_CH10", "Offsetwert1_CH10", "Offsetwert2_CH10", "Grenze_Masse_unten_CH10", "Grenze_Masse_oben_CH10", "Status_der_Messung_CH10"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;

        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;
        let status = error_matching(&entry.status[3]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;

        worksheet.write_number(row, 38, entry.integral[4] as f64, None)?;
        worksheet.write_number(row, 39, entry.mass[4] as f64, None)?;
        worksheet.write_number(row, 40, entry.offset[4] as f64, None)?;
        worksheet.write_number(row, 41, entry.offset1[4] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset2[4] as f64, None)?;
        worksheet.write_number(row, 43, entry.tolerance_bottom[4] as f64, None)?;
        worksheet.write_number(row, 44, entry.tolerance_top[4] as f64, None)?;
        let status = error_matching(&entry.status[4]).await?;
        worksheet.write_string(row, 44, &status.join(","), None)?;

        worksheet.write_number(row, 46, entry.integral[5] as f64, None)?;
        worksheet.write_number(row, 47, entry.mass[5] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset[5] as f64, None)?;
        worksheet.write_number(row, 49, entry.offset1[5] as f64, None)?;
        worksheet.write_number(row, 50, entry.offset2[5] as f64, None)?;
        worksheet.write_number(row, 51, entry.tolerance_bottom[5] as f64, None)?;
        worksheet.write_number(row, 52, entry.tolerance_top[5] as f64, None)?;
        let status = error_matching(&entry.status[5]).await?;
        worksheet.write_string(row, 53, &status.join(","), None)?;

        worksheet.write_number(row, 54, entry.integral[6] as f64, None)?;
        worksheet.write_number(row, 55, entry.mass[6] as f64, None)?;
        worksheet.write_number(row, 56, entry.offset[6] as f64, None)?;
        worksheet.write_number(row, 57, entry.offset1[6] as f64, None)?;
        worksheet.write_number(row, 58, entry.offset2[6] as f64, None)?;
        worksheet.write_number(row, 59, entry.tolerance_bottom[6] as f64, None)?;
        worksheet.write_number(row, 60, entry.tolerance_top[6] as f64, None)?;
        let status = error_matching(&entry.status[6]).await?;
        worksheet.write_string(row, 61, &status.join(","), None)?;

        worksheet.write_number(row, 62, entry.integral[7] as f64, None)?;
        worksheet.write_number(row, 63, entry.mass[7] as f64, None)?;
        worksheet.write_number(row, 64, entry.offset[7] as f64, None)?;
        worksheet.write_number(row, 65, entry.offset1[7] as f64, None)?;
        worksheet.write_number(row, 66, entry.offset2[7] as f64, None)?;
        worksheet.write_number(row, 67, entry.tolerance_bottom[7] as f64, None)?;
        worksheet.write_number(row, 68, entry.tolerance_top[7] as f64, None)?;
        let status = error_matching(&entry.status[7]).await?;
        worksheet.write_string(row, 69, &status.join(","), None)?;

        worksheet.write_number(row, 70, entry.integral[8] as f64, None)?;
        worksheet.write_number(row, 71, entry.mass[8] as f64, None)?;
        worksheet.write_number(row, 72, entry.offset[8] as f64, None)?;
        worksheet.write_number(row, 73, entry.offset1[8] as f64, None)?;
        worksheet.write_number(row, 74, entry.offset2[8] as f64, None)?;
        worksheet.write_number(row, 75, entry.tolerance_bottom[8] as f64, None)?;
        worksheet.write_number(row, 76, entry.tolerance_top[8] as f64, None)?;
        let status = error_matching(&entry.status[8]).await?;
        worksheet.write_string(row, 77, &status.join(","), None)?;

        worksheet.write_number(row, 78, entry.integral[9] as f64, None)?;
        worksheet.write_number(row, 79, entry.mass[9] as f64, None)?;
        worksheet.write_number(row, 80, entry.offset[9] as f64, None)?;
        worksheet.write_number(row, 81, entry.offset1[9] as f64, None)?;
        worksheet.write_number(row, 82, entry.offset2[9] as f64, None)?;
        worksheet.write_number(row, 83, entry.tolerance_bottom[9] as f64, None)?;
        worksheet.write_number(row, 84, entry.tolerance_top[9] as f64, None)?;
        let status = error_matching(&entry.status[9]).await?;
        worksheet.write_string(row, 85, &status.join(","), None)?;

        worksheet.write_number(row, 86, entry.integral[10] as f64, None)?;
        worksheet.write_number(row, 87, entry.mass[10] as f64, None)?;
        worksheet.write_number(row, 88, entry.offset[10] as f64, None)?;
        worksheet.write_number(row, 89, entry.offset1[10] as f64, None)?;
        worksheet.write_number(row, 90, entry.offset2[10] as f64, None)?;
        worksheet.write_number(row, 91, entry.tolerance_bottom[10] as f64, None)?;
        worksheet.write_number(row, 92, entry.tolerance_top[10] as f64, None)?;
        let status = error_matching(&entry.status[10]).await?;
        worksheet.write_string(row, 93, &status.join(","), None)?;

    }
    Ok(())
}

pub async fn store_measurement_data_as_xlsx_12CH(data: &Vec<db::UdpTag41>,name: &str, ip: &str) -> Result<(), Box<dyn Error>> {
    // Create the workbook and worksheet
    let workbook = Workbook::new(name)?;
    let mut worksheet = workbook.add_worksheet(None)?;

    let headers = ["Zeitstempel Erstellt", "Sensor IP", "Fortlaufender Zähler", "Zeitstempel des letzten Offsetabgleichs", "Dauer des letzten Offsetabgleichs", "Zeitstempel Messung",
     "Integral_CH0", "Masse_CHO", "Offsetwert_CH0", "Offsetwert1_CH0", "Offsetwert2_CH0", "Grenze_Masse_unten_CH0", "Grenze_Masse_oben_CH0", "Status_der_Messung_CH0",
     "Integral_CH1", "Masse_CH1", "Offsetwert_CH1", "Offsetwert1_CH1", "Offsetwert2_CH1", "Grenze_Masse_unten_CH1", "Grenze_Masse_oben_CH1", "Status_der_Messung_CH1",
     "Integral_CH2", "Masse_CH2", "Offsetwert_CH2", "Offsetwert1_CH2", "Offsetwert2_CH2", "Grenze_Masse_unten_CH2", "Grenze_Masse_oben_CH2", "Status_der_Messung_CH2",
     "Integral_CH3", "Masse_CH3", "Offsetwert_CH3", "Offsetwert1_CH3", "Offsetwert2_CH3", "Grenze_Masse_unten_CH3", "Grenze_Masse_oben_CH3", "Status_der_Messung_CH3",
     "Integral_CH4", "Masse_CH4", "Offsetwert_CH4", "Offsetwert1_CH4", "Offsetwert2_CH4", "Grenze_Masse_unten_CH4", "Grenze_Masse_oben_CH4", "Status_der_Messung_CH4",
     "Integral_CH5", "Masse_CH5", "Offsetwert_CH5", "Offsetwert1_CH5", "Offsetwert2_CH5", "Grenze_Masse_unten_CH5", "Grenze_Masse_oben_CH5", "Status_der_Messung_CH5",
     "Integral_CH6", "Masse_CH6", "Offsetwert_CH6", "Offsetwert1_CH6", "Offsetwert2_CH6", "Grenze_Masse_unten_CH6", "Grenze_Masse_oben_CH6", "Status_der_Messung_CH6",
     "Integral_CH7", "Masse_CH7", "Offsetwert_CH7", "Offsetwert1_CH7", "Offsetwert2_CH7", "Grenze_Masse_unten_CH7", "Grenze_Masse_oben_CH7", "Status_der_Messung_CH7",
     "Integral_CH8", "Masse_CH8", "Offsetwert_CH8", "Offsetwert1_CH8", "Offsetwert2_CH8", "Grenze_Masse_unten_CH8", "Grenze_Masse_oben_CH8", "Status_der_Messung_CH8",
     "Integral_CH9", "Masse_CH9", "Offsetwert_CH9", "Offsetwert1_CH9", "Offsetwert2_CH9", "Grenze_Masse_unten_CH9", "Grenze_Masse_oben_CH9", "Status_der_Messung_CH9",
     "Integral_CH10", "Masse_CH10", "Offsetwert_CH10", "Offsetwert1_CH10", "Offsetwert2_CH10", "Grenze_Masse_unten_CH10", "Grenze_Masse_oben_CH10", "Status_der_Messung_CH10",
     "Integral_CH11", "Masse_CH11", "Offsetwert_CH11", "Offsetwert1_CH11", "Offsetwert2_CH11", "Grenze_Masse_unten_CH11", "Grenze_Masse_oben_CH11", "Status_der_Messung_CH11"];

    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, None)?;

    }

    for (i, entry) in data.iter().enumerate() {
        let row = (i + 1) as u32; // Start at the second row
        
        worksheet.write_string(row, 0, &entry.created, None)?;
        worksheet.write_string(row, 1, ip, None)?;
        worksheet.write_number(row, 2, entry.counter as f64, None)?;
        worksheet.write_string(row, 5, &entry.timestamp, None)?;

        worksheet.write_number(row, 6, entry.integral[0] as f64, None)?;
        worksheet.write_number(row, 7, entry.mass[0] as f64, None)?;
        worksheet.write_number(row, 8, entry.offset[0] as f64, None)?;
        worksheet.write_number(row, 9, entry.offset1[0] as f64, None)?;
        worksheet.write_number(row, 10, entry.offset2[0] as f64, None)?;
        worksheet.write_number(row, 11, entry.tolerance_bottom[0] as f64, None)?;
        worksheet.write_number(row, 12, entry.tolerance_top[0] as f64, None)?;
        let status = error_matching(&entry.status[0]).await?;
        worksheet.write_string(row, 13, &status.join(","), None)?;

        worksheet.write_number(row, 14, entry.integral[1] as f64, None)?;
        worksheet.write_number(row, 15, entry.mass[1] as f64, None)?;
        worksheet.write_number(row, 16, entry.offset[1] as f64, None)?;
        worksheet.write_number(row, 17, entry.offset1[1] as f64, None)?;
        worksheet.write_number(row, 18, entry.offset2[1] as f64, None)?;
        worksheet.write_number(row, 19, entry.tolerance_bottom[1] as f64, None)?;
        worksheet.write_number(row, 20, entry.tolerance_top[1] as f64, None)?;
        let status = error_matching(&entry.status[1]).await?;
        worksheet.write_string(row, 21, &status.join(","), None)?;

        worksheet.write_number(row, 22, entry.integral[2] as f64, None)?;
        worksheet.write_number(row, 23, entry.mass[2] as f64, None)?;
        worksheet.write_number(row, 24, entry.offset[2] as f64, None)?;
        worksheet.write_number(row, 25, entry.offset1[2] as f64, None)?;
        worksheet.write_number(row, 26, entry.offset2[2] as f64, None)?;
        worksheet.write_number(row, 27, entry.tolerance_bottom[2] as f64, None)?;
        worksheet.write_number(row, 28, entry.tolerance_top[2] as f64, None)?;
        let status = error_matching(&entry.status[2]).await?;
        worksheet.write_string(row, 29, &status.join(","), None)?;

        worksheet.write_number(row, 30, entry.integral[3] as f64, None)?;
        worksheet.write_number(row, 31, entry.mass[3] as f64, None)?;
        worksheet.write_number(row, 32, entry.offset[3] as f64, None)?;
        worksheet.write_number(row, 33, entry.offset1[3] as f64, None)?;
        worksheet.write_number(row, 34, entry.offset2[3] as f64, None)?;
        worksheet.write_number(row, 35, entry.tolerance_bottom[3] as f64, None)?;
        worksheet.write_number(row, 36, entry.tolerance_top[3] as f64, None)?;
        let status = error_matching(&entry.status[3]).await?;
        worksheet.write_string(row, 37, &status.join(","), None)?;

        worksheet.write_number(row, 38, entry.integral[4] as f64, None)?;
        worksheet.write_number(row, 39, entry.mass[4] as f64, None)?;
        worksheet.write_number(row, 40, entry.offset[4] as f64, None)?;
        worksheet.write_number(row, 41, entry.offset1[4] as f64, None)?;
        worksheet.write_number(row, 42, entry.offset2[4] as f64, None)?;
        worksheet.write_number(row, 43, entry.tolerance_bottom[4] as f64, None)?;
        worksheet.write_number(row, 44, entry.tolerance_top[4] as f64, None)?;
        let status = error_matching(&entry.status[4]).await?;
        worksheet.write_string(row, 45, &status.join(","), None)?;

        worksheet.write_number(row, 46, entry.integral[5] as f64, None)?;
        worksheet.write_number(row, 47, entry.mass[5] as f64, None)?;
        worksheet.write_number(row, 48, entry.offset[5] as f64, None)?;
        worksheet.write_number(row, 49, entry.offset1[5] as f64, None)?;
        worksheet.write_number(row, 50, entry.offset2[5] as f64, None)?;
        worksheet.write_number(row, 51, entry.tolerance_bottom[5] as f64, None)?;
        worksheet.write_number(row, 52, entry.tolerance_top[5] as f64, None)?;
        let status = error_matching(&entry.status[5]).await?;
        worksheet.write_string(row, 53, &status.join(","), None)?;

        worksheet.write_number(row, 54, entry.integral[6] as f64, None)?;
        worksheet.write_number(row, 55, entry.mass[6] as f64, None)?;
        worksheet.write_number(row, 56, entry.offset[6] as f64, None)?;
        worksheet.write_number(row, 57, entry.offset1[6] as f64, None)?;
        worksheet.write_number(row, 58, entry.offset2[6] as f64, None)?;
        worksheet.write_number(row, 59, entry.tolerance_bottom[6] as f64, None)?;
        worksheet.write_number(row, 60, entry.tolerance_top[6] as f64, None)?;
        let status = error_matching(&entry.status[6]).await?;
        worksheet.write_string(row, 61, &status.join(","), None)?;

        worksheet.write_number(row, 62, entry.integral[7] as f64, None)?;
        worksheet.write_number(row, 63, entry.mass[7] as f64, None)?;
        worksheet.write_number(row, 64, entry.offset[7] as f64, None)?;
        worksheet.write_number(row, 65, entry.offset1[7] as f64, None)?;
        worksheet.write_number(row, 66, entry.offset2[7] as f64, None)?;
        worksheet.write_number(row, 67, entry.tolerance_bottom[7] as f64, None)?;
        worksheet.write_number(row, 68, entry.tolerance_top[7] as f64, None)?;
        let status = error_matching(&entry.status[7]).await?;
        worksheet.write_string(row, 69, &status.join(","), None)?;

        worksheet.write_number(row, 70, entry.integral[8] as f64, None)?;
        worksheet.write_number(row, 71, entry.mass[8] as f64, None)?;
        worksheet.write_number(row, 72, entry.offset[8] as f64, None)?;
        worksheet.write_number(row, 73, entry.offset1[8] as f64, None)?;
        worksheet.write_number(row, 74, entry.offset2[8] as f64, None)?;
        worksheet.write_number(row, 75, entry.tolerance_bottom[8] as f64, None)?;
        worksheet.write_number(row, 76, entry.tolerance_top[8] as f64, None)?;
        let status = error_matching(&entry.status[8]).await?;
        worksheet.write_string(row, 78, &status.join(","), None)?;

        worksheet.write_number(row, 78, entry.integral[9] as f64, None)?;
        worksheet.write_number(row, 79, entry.mass[9] as f64, None)?;
        worksheet.write_number(row, 80, entry.offset[9] as f64, None)?;
        worksheet.write_number(row, 81, entry.offset1[9] as f64, None)?;
        worksheet.write_number(row, 82, entry.offset2[9] as f64, None)?;
        worksheet.write_number(row, 83, entry.tolerance_bottom[9] as f64, None)?;
        worksheet.write_number(row, 84, entry.tolerance_top[9] as f64, None)?;
        let status = error_matching(&entry.status[9]).await?;
        worksheet.write_string(row, 85, &status.join(","), None)?;

        worksheet.write_number(row, 86, entry.integral[10] as f64, None)?;
        worksheet.write_number(row, 87, entry.mass[10] as f64, None)?;
        worksheet.write_number(row, 88, entry.offset[10] as f64, None)?;
        worksheet.write_number(row, 89, entry.offset1[10] as f64, None)?;
        worksheet.write_number(row, 90, entry.offset2[10] as f64, None)?;
        worksheet.write_number(row, 91, entry.tolerance_bottom[10] as f64, None)?;
        worksheet.write_number(row, 92, entry.tolerance_top[10] as f64, None)?;
        let status = error_matching(&entry.status[10]).await?;
        worksheet.write_string(row, 93, &status.join(","), None)?;

        worksheet.write_number(row, 94, entry.integral[11] as f64, None)?;
        worksheet.write_number(row, 95, entry.mass[11] as f64, None)?;
        worksheet.write_number(row, 96, entry.offset[11] as f64, None)?;
        worksheet.write_number(row, 97, entry.offset1[11] as f64, None)?;
        worksheet.write_number(row, 98, entry.offset2[11] as f64, None)?;
        worksheet.write_number(row, 99, entry.tolerance_bottom[11] as f64, None)?;
        worksheet.write_number(row, 100, entry.tolerance_top[11] as f64, None)?;
        let status = error_matching(&entry.status[11]).await?;
        worksheet.write_string(row, 101, &status.join(","), None)?;

    }
    Ok(())
}