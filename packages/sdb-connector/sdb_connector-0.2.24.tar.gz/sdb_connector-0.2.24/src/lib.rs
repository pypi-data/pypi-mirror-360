use std::error::Error;
use pyo3::prelude::*;

mod export;
mod db;
mod process;


#[pymodule]
fn sdb_connector(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(select_additional_info_data, m)?)?;
    m.add_function(wrap_pyfunction!(select_measurement_data, m)?)?;
    m.add_function(wrap_pyfunction!(select_raw_data, m)?)?;
    // m.add_function(wrap_pyfunction!(select_general_info_data, m)?)?;
    Ok(())
}


#[pyfunction]
fn select_additional_info_data(ip: &str, port: &str,
    user: &str, pw:&str, namespace: &str, db_name: &str,
    table_name: &str, run_id: &str, path_name:&str, select_type: u8) -> PyResult<Vec<(u64, u16, u8, u16, u16, u16, u16, u16, u16, String)>> {
    // Create a Tokio runtime and block on the async function
    let rt = match tokio::runtime::Runtime::new() {
        Ok(rt) => rt,
        Err(e) => {
            println!("Error creating runtime: {:?}", e);
            return Err(PyErr::new::<pyo3::exceptions::PyException, _>("Error creating runtime"));
        }
    };
    let data = match rt.block_on(select_additional_info_data_async(ip, port,user, pw, namespace, db_name, table_name,run_id, path_name, select_type)) {
        Ok(data) => data,
        Err(e) => {
            println!("Error selecting additional info data: {:?}", e);
            return Err(PyErr::new::<pyo3::exceptions::PyException, _>("Error selecting additional info data"));
        }
    };
    Ok(data)
}

// #[pyfunction]
// fn select_general_info_data(
//     ip: &str,
//     port: &str,
//     user: &str,
//     pw: &str,
//     namespace: &str,
//     db_name: &str,
//     table_name: &str,
//     run_id: &str,
//     path_name: &str,
//     select_type: u8,
// ) -> PyResult<Vec<(u64, String, String, String, String, String, String,String, u8, u16, u32, String, u32, String, u16, u16)>> {
//     let rt = tokio::runtime::Runtime::new()
//         .map_err(|e| PyErr::new::<pyo3::exceptions::PyException, _>(e.to_string()))?;

//     let data = rt.block_on(select_general_info_data_async(
//         ip, port, user, pw, namespace, db_name, table_name, run_id, path_name, select_type,
//     )).map_err(|e| PyErr::new::<pyo3::exceptions::PyException, _>(e.to_string()))?;

//     Ok(data)
// }

#[pyfunction]
fn select_measurement_data(ip: &str, port: &str,
    user: &str, pw:&str, namespace: &str, db_name: &str,
    table_name: &str, run_id: &str, path_name: &str, select_type: u8) -> PyResult<Vec<(u64, u8, u64, u64, u16, u16, u16, u16, u16, String, Vec<String>)>> {
    // Create a Tokio runtime and block on the async function
    let rt = match tokio::runtime::Runtime::new() {
        Ok(rt) => rt,
        Err(e) => {
            println!("Error creating runtime: {:?}", e);
            return Err(PyErr::new::<pyo3::exceptions::PyException, _>("Error creating runtime"));
        }
    };
    let data = match rt.block_on(select_measurement_data_async(ip, port,user, pw, namespace, db_name, table_name,run_id, path_name, select_type)) {
        Ok(data) => data,
        Err(e) => {
            println!("Error selecting measurement data: {:?}", e);
            return Err(PyErr::new::<pyo3::exceptions::PyException, _>("Error selecting measurement data"));
        }
    };
    Ok(data)
}

#[pyfunction]
fn select_raw_data(ip: &str, port: &str,
    user: &str, pw:&str, namespace: &str, db_name: &str,
    table_name: &str, run_id: &str) -> PyResult<Vec<(u64, u8, i32, String, u32)>> {
    // Create a Tokio runtime and block on the async function
    let rt = match tokio::runtime::Runtime::new() {
        Ok(rt) => rt,
        Err(e) => {
            println!("Error creating runtime: {:?}", e);
            return Err(PyErr::new::<pyo3::exceptions::PyException, _>("Error creating runtime"));
        }
    };
    let data = match rt.block_on(select_raw_data_async(ip, port,user, pw, namespace, db_name, table_name,run_id)) {
        Ok(data) => data,
        Err(e) => {
            println!("Error selecting raw data: {:?}", e);
            return Err(PyErr::new::<pyo3::exceptions::PyException, _>("Error selecting raw data"));
        }
    };
    Ok(data)
}

// pub async fn select_general_info_data_async(
//     ip: &str,
//     port: &str,
//     user: &str,
//     pw: &str,
//     namespace: &str,
//     db_name: &str,
//     table_name: &str,
//     run_id: &str,
//     path_name: &str,
//     select_type: u8
// ) -> Result<Vec<(u64, String, String, String, String, String, String,String, u8, u16, u32, String, u32, String, u16, u16)>, Box<dyn Error>> {
//     let db = db::connect_to_db(ip, port, user, pw, namespace, db_name).await?;
//     let result = db::query_general_information(&db, table_name, run_id).await?;
//     let data = process::process_general_information_data(result, select_type).await?;
//     Ok(data)
// }

// Main function that uses both helper functions
pub async fn select_additional_info_data_async(
    ip: &str,
    port: &str,
    user: &str,
    pw: &str,
    namespace: &str,
    db_name: &str,
    table_name: &str,
    run_id: &str,
    path_name: &str,
    select_type: u8
) -> Result<Vec<(u64, u16, u8, u16, u16, u16, u16, u16, u16, String)>, Box<dyn Error>> {
    let db = db::connect_to_db(ip, port, user, pw, namespace, db_name).await?;
    // Query the general information from the database
    let mut general_info_result = db::query_amv_static_info(&db, "amv_static_info", run_id).await?;
    let general_info : Vec<db::AmvStaticInfo> = match general_info_result.take(0) {
        Ok(data) => data,
        Err(e) => {
            println!("Error selecting measurement data: {:?}", e);
            return Err(Box::new(e));
        }
    };
    let ip = format!("{}.{}.{}.{}", general_info[0].ip_address[0], general_info[0].ip_address[1], general_info[0].ip_address[2], general_info[0].ip_address[3]);

    let number_of_channels = general_info[0].number_of_channels;
    let result = db::query_additonal_info_data(&db, table_name, run_id).await?;
    let data = process::process_additonal_info_data(result, &ip,path_name, select_type, number_of_channels).await?;
    Ok(data)
}

// Main function that uses both helper functions
pub async fn select_measurement_data_async(
    ip: &str,
    port: &str,
    user: &str,
    pw: &str,
    namespace: &str,
    db_name: &str,
    table_name: &str,
    run_id: &str,
    path_name: &str, 
    select_type: u8,
) -> Result<Vec<(u64, u8, u64, u64, u16, u16, u16, u16, u16, String, Vec<String>, )>, Box<dyn Error>> {
    let db = db::connect_to_db(ip, port, user, pw, namespace, db_name).await?;
     
    let mut general_info_result = db::query_amv_static_info(&db, "amv_static_info", run_id).await?;
    let general_info : Vec<db::AmvStaticInfo> = match general_info_result.take(0) {
        Ok(data) => data,
        Err(e) => {
            println!("Error selecting general_info: {:?}", e);
            return Err(Box::new(e));
        }
    };
    let ip = format!("{}.{}.{}.{}", general_info[0].ip_address[0], general_info[0].ip_address[1], general_info[0].ip_address[2], general_info[0].ip_address[3]);
    let number_of_channels = general_info[0].number_of_channels;
    let result = db::query_measurement_data(&db, table_name, run_id).await?;
    let data = process::process_measurement_data(result, &ip, path_name, select_type, number_of_channels).await?;
    Ok(data)
}


// Main function that uses both helper functions
pub async fn select_raw_data_async(
    ip: &str,
    port: &str,
    user: &str,
    pw: &str,
    namespace: &str,
    db_name: &str,
    table_name: &str,
    run_id: &str
) -> Result<Vec<(u64, u8, i32, String, u32)>, Box<dyn Error>> {
    let db = db::connect_to_db(ip, port, user, pw, namespace, db_name).await?;
    let result = db::query_raw_data(&db, table_name, run_id).await?;
    let data = process::process_raw_data(result).await?;
    Ok(data)
}



    