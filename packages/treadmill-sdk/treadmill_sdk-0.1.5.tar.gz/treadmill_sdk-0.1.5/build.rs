extern crate bindgen;
// extern crate cc;

// use cfg_if::cfg_if;
use std::fs::{copy, OpenOptions};
use std::io::BufWriter;
use std::path::Path;
// use std::process::Command;
use std::{env, fs, io::Write};

fn main() {
  // let lib_name = "crc";
  // cc::Build::new().file("src/c/crc.c").compile(lib_name);

  // let header_path = "src/c/crc.h";
  // let bindings = bindgen::Builder::default()
  //   .header(header_path)
  //   .generate()
  //   .expect("Unable to generate bindings");
  // let output_path = Path::new("src").join("generated/crc_bindings.rs");
  // bindings
  //   .write_to_file(&output_path)
  //   .expect("Couldn't write bindings!");

  if env::var("GITHUB_ACTIONS").is_ok() {
    return;
  }

  if env::var("CENTOS").is_ok() {
    return;
  }

  // println!("cargo:rerun-if-changed=build.rs");
  // csbindgen::Builder::default()
  //   .input_extern_file("src/encrypt/callback_c.rs")
  //   .csharp_dll_name("treadmill_sdk") // required
  //   .csharp_class_name("TreadmillSDK") // optional, default: NativeMethods
  //   .csharp_namespace("Treadmill") // optional, default: CsBindgen
  //   .csharp_class_accessibility("internal") // optional, default: internal
  //   .csharp_entry_point_prefix("") // optional, default: ""
  //   .csharp_method_prefix("") // optional, default: ""
  //   .csharp_use_function_pointer(false) // optional, default: true
  //   .csharp_disable_emit_dll_name(false) // optional, default: false
  //   // .csharp_imported_namespaces("MyLib") // optional, default: empty
  //   .csharp_generate_const_filter(|_| false) // optional, default: `|_|false`
  //   .csharp_dll_name_if("UNITY_IOS && !UNITY_EDITOR", "__Internal") // optional, default: ""
  //   // .csharp_type_rename(|rust_type_name| match rust_type_name {
  //   //   // optional, default: `|x| x`
  //   //   "FfiConfiguration".to_string() => "Configuration".into(),
  //   //   _ => x,
  //   // })
  //   .generate_csharp_file("./dist/unity/TreadmillSDK.cs") // required
  //   .unwrap();

  // pyo3_build_config::configure().unwrap();
  // println!("cargo:rustc-link-lib=python3.10");
  // println!("cargo:rustc-link-search=native=/opt/homebrew/Caskroom/miniconda/base/envs/py310/lib/");

  // 重新编译触发机制
  println!("cargo:rerun-if-changed=proto3/");

  // 编译并复制 treadmill proto
  let tml_proto_files = ["proto3/treadmill/treadmill_message.proto"];
  let tml_include_dirs = ["proto3/treadmill"];
  compile_and_copy_protos(&tml_proto_files, &tml_include_dirs, "treadmill");

  // 格式化生成的代码
  // Command::new("cargo")
  //   .arg("fmt")
  //   .spawn()
  //   .expect("Failed to format code");
}

#[allow(dead_code, unused_variables)]
fn compile_and_copy_protos(proto_files: &[&str], proto_include_dirs: &[&str], package_name: &str) {
  if env::var("CARGO_CFG_RELEASE").is_ok() {
    return;
  }

  if env::var("CENTOS").is_ok() {
    return;
  }

  if cfg!(target_os = "linux") {
    return;
  }

  // #[allow(unreachable_code)]
  let out_dir = env::var("OUT_DIR").expect("OUT_DIR not set");
  println!("out_dir: {}", out_dir);

  // Tell cargo to recompile if any of these proto files are changed
  // for proto_file in proto_files {
  //     println!("cargo:rerun-if-changed={}", proto_file);
  // }

  let descriptor_path = Path::new(&out_dir).join("proto_descriptor.bin");
  let package = format!("tech.brainco.{}", package_name);

  prost_build::Config::new()
    .file_descriptor_set_path(&descriptor_path)
    .compile_well_known_types()
    .extern_path(".google.protobuf", "::pbjson_types")
    // .type_attribute(".", format!("#[prost(message, package = \"{}\")]", package))
    .compile_protos(proto_files, proto_include_dirs)
    .expect("Failed to compile protos");

  let output_name = format!("{}_proto", package_name);
  let descriptor_set = std::fs::read(descriptor_path).unwrap();
  let mut binding = pbjson_build::Builder::new();
  let builder = binding.register_descriptors(&descriptor_set).unwrap();
  // if cfg!(feature = "ignore-unknown-fields") {
  //     builder.ignore_unknown_fields();
  // }
  // if cfg!(feature = "btree") {
  //     builder.btree_map([".test"]);
  // }
  // if cfg!(feature = "emit-fields") {
  //     builder.emit_fields();
  // }
  // if cfg!(feature = "use-integers-for-enums") {
  //     builder.use_integers_for_enums();
  // }
  // if cfg!(feature = "preserve-proto-field-names") {
  //     builder.preserve_proto_field_names();
  // }

  builder.build(&[format!(".{}", package)]).unwrap();

  // 自动生成模块文件的路径
  let module_path = Path::new(&out_dir).join(format!("{}.rs", package));
  println!("module_path {:?}", module_path);
  // 检查生成的文件是否存在
  if !module_path.exists() {
    panic!("Generated file does not exist: {:?}", module_path);
  }
  // 将生成的模块文件复制到指定的输出文件
  let output_path = Path::new("src").join(format!("generated/{}.rs", output_name));
  copy(&module_path, &output_path).expect("Failed to copy generated proto file");

  let module_path = Path::new(&out_dir).join(format!("tech.brainco.{}.serde.rs", package_name));
  if !module_path.exists() {
    panic!("Generated serde file does not exist: {:?}", module_path);
  }
  let output_path = Path::new("src").join(format!("generated/{}_serde.rs", output_name));
  copy(&module_path, &output_path).expect("Failed to copy generated serde proto file");

  let mut file = OpenOptions::new()
    .write(true)
    .truncate(true)
    .create(true)
    .open(&output_path)
    .unwrap();
  let mut writer = BufWriter::new(&mut file);

  // Write use statements manually
  writeln!(writer, "use crate::generated::{}::*;", output_name).unwrap();
  // writeln!(writer, "use serde::{{Serialize, Deserialize}};")?;

  // Write the rest of the content of the generated file
  let generated_content = fs::read_to_string(module_path).unwrap();
  write!(writer, "{}", generated_content).unwrap();
}
