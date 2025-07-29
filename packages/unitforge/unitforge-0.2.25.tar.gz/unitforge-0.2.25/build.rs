use regex::Regex;
use std::fs::File;
use std::path::PathBuf;
use std::{env, fs, io::Write, path::Path};

fn main() {
    let quantities_template_path = "src/quantities.template.rs".to_string();
    let vector_template_path = "src/small_linalg/bindings/vector3_py.template.rs".to_string();
    let matrix_template_path = "src/small_linalg/bindings/matrix3_py.template.rs".to_string();
    println!("cargo:rerun-if-changed=src/quantities/");
    println!("cargo:rerun-if-changed={}", quantities_template_path);
    println!("cargo:rerun-if-changed={}", vector_template_path);
    println!("cargo:rerun-if-changed={}", matrix_template_path);

    let out_dir = env::var("OUT_DIR").unwrap();
    let quantity_macro_re = Regex::new(r"impl_quantity!\s*\(\s*(\w+)").unwrap();
    let quantities_dir = Path::new("src/quantities");
    let quantity_structs =
        extract_quantity_struct_names_from_dir(quantities_dir, &quantity_macro_re);

    write_quantity_code(
        &Path::new(&out_dir).join("quantities.rs"),
        &quantity_structs,
        quantities_template_path,
    );
    if env::var("CARGO_FEATURE_PYO3").is_ok() {
        write_vector_code(
            &Path::new(&out_dir).join("vector3_py.rs"),
            &quantity_structs,
            vector_template_path,
        );
        write_matrix_code(
            &Path::new(&out_dir).join("matrix3_py.rs"),
            &quantity_structs,
            matrix_template_path,
        );
        write_module_definition(
            &Path::new(&out_dir).join("python_module_definition.rs"),
            &quantity_structs,
        );
    }
}

fn extract_quantity_struct_names_from_dir(dir: &Path, regex: &Regex) -> Vec<(String, String)> {
    let mut structs = Vec::new();

    for entry in fs::read_dir(dir).expect("Can't read src/quantities") {
        let entry = entry.unwrap();
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) == Some("rs") {
            let content = fs::read_to_string(&path).expect("Failed to read quantity file");
            for caps in regex.captures_iter(&content) {
                let struct_name = caps[1].to_string();
                structs.push((struct_name, content.clone()));
            }
        }
    }
    structs
}

fn camel_to_snake(input: &str) -> String {
    let mut result = String::with_capacity(input.len());
    for (i, c) in input.char_indices() {
        if c.is_uppercase() {
            if i != 0 {
                result.push('_');
            }
            result.extend(c.to_lowercase());
        } else {
            result.push(c);
        }
    }
    result
}

fn write_quantity_code(
    dest_path: &PathBuf,
    quantity_structs: &Vec<(String, String)>,
    quantities_template_path: String,
) {
    let template = fs::read_to_string(quantities_template_path)
        .expect("Failed to read quantities.template.rs");

    let mut quantity_variants = String::new();
    let mut quantity_to_variants = String::new();
    let mut quantity_fmt_matches = String::new();
    let mut quantity_comparisons = String::new();
    let mut unit_variants = String::new();
    let mut to_quantity_variants = String::new();
    let mut quantity_abs_variants = String::new();
    let mut unit_name_variants = String::new();
    let mut extract_quantity_matches = String::new();
    let mut extract_unit_matches = String::new();
    let mut to_pyobject_matches = String::new();
    let mut mul_matches = String::new();
    let mut div_matches = String::new();
    let mut base_quantity_matches = String::new();
    let mut add_matches = String::new();
    let mut sub_matches = String::new();
    let mut sqrt_matches = String::new();

    let mul_macro_re = Regex::new(r"impl_mul!\(\s*(\w+),\s*(\w+),\s*(\w+)\)").unwrap();
    let div_macro_re = Regex::new(r"impl_div!\(\s*(\w+),\s*(\w+),\s*(\w+)\)").unwrap();
    let mul_with_self_macro_re = Regex::new(r"impl_mul_with_self!\(\s*(\w+),\s*(\w+)\)").unwrap();
    let div_with_self_to_f64_macro_re =
        Regex::new(r"impl_div_with_self_to_f64!\(\s*(\w+)\)").unwrap();
    let sqrt_macro_re = Regex::new(r"impl_sqrt!\(\s*(\w+),\s*(\w+)\s*\)").unwrap();

    let mut first = true;
    for (struct_name, content) in quantity_structs {
        quantity_variants += &format!("    {}Quantity({}),\n", struct_name, struct_name);
        quantity_to_variants += &format!("            (Quantity::{}Quantity(value), Unit::{}Unit(unit)) => Ok(value.to(unit)),\n", struct_name, struct_name);
        quantity_fmt_matches += &format!(
            "            Quantity::{}Quantity(v) => write!(f, \"{{}}\", v),\n",
            struct_name
        );
        quantity_comparisons += &format!(
            "            ({}Quantity(lhs), {}Quantity(rhs)) => lhs.partial_cmp(rhs),\n",
            struct_name, struct_name
        );
        unit_variants += &format!("    {}Unit({}Unit),\n", struct_name, struct_name);
        to_quantity_variants += &format!(
            "            Unit::{}Unit(unit) => Quantity::{}Quantity({}::new(value, *unit)),\n",
            struct_name, struct_name, struct_name
        );
        quantity_abs_variants += &format!(
            "            Quantity::{}Quantity(value) => Quantity::{}Quantity(value.abs()),\n",
            struct_name, struct_name
        );
        unit_name_variants += &format!(
            "            Unit::{}Unit(unit) => unit.name(),\n",
            struct_name
        );
        extract_quantity_matches += &format!(
            "        else if let Ok(inner) = v.extract::<{}>() {{\n            Ok(Quantity::{}Quantity(inner))\n        }}\n",
            struct_name, struct_name
        );
        let prefix = if first { "" } else { "        else " };
        extract_unit_matches += &format!(
            "{}if let Ok(inner) = v.extract::<{}Unit>() {{\n    Ok(Unit::{}Unit(inner))\n}}\n",
            prefix, struct_name, struct_name
        );
        to_pyobject_matches += &format!(
            "            Quantity::{}Quantity(v) => v.into_py(py),\n",
            struct_name
        );
        mul_matches += &format!(
            "                (FloatQuantity(v_lhs), {0}Quantity(v_rhs)) => Ok({0}Quantity(*v_lhs * *v_rhs)),\n",
            struct_name
        );
        div_matches += &format!(
            "            ({0}Quantity(v_lhs), FloatQuantity(v_rhs)) => Ok({0}Quantity(v_lhs / v_rhs)),\n",
            struct_name
        );
        add_matches += &format!(
            "            ({0}Quantity(v_lhs), {0}Quantity(v_rhs)) => Ok({0}Quantity(v_lhs + v_rhs)),\n",
            struct_name
        );
        sub_matches += &format!(
            "            ({0}Quantity(v_lhs), {0}Quantity(v_rhs)) => Ok({0}Quantity(v_lhs - v_rhs)),\n",
            struct_name
        );

        let lowercase_name = camel_to_snake(struct_name);
        base_quantity_matches += &format!(
            "    pub fn extract_{}(&self) -> Result<{}, String> {{
        match self {{
            Quantity::{}Quantity(v) => Ok(*v),
            _ => Err(\"Cannot extract {} from Quantity enum\".into()),
        }}
    }}\n\n",
            lowercase_name, struct_name, struct_name, struct_name
        );

        for caps in mul_macro_re.captures_iter(content) {
            let lhs = &caps[1];
            let rhs = &caps[2];
            let mut result = caps[3].to_string();
            if result == "f64" {
                result = "Float".to_string();
            }
            mul_matches += &format!(
                "                ({0}Quantity(v_lhs), {1}Quantity(v_rhs)) => Ok({2}Quantity(*v_lhs * *v_rhs)),\n",
                lhs, rhs, result
            );
        }

        for caps in div_macro_re.captures_iter(content) {
            let lhs = &caps[1];
            let rhs = &caps[2];
            let mut result = caps[3].to_string();
            if result == "f64" {
                result = "Float".to_string();
            }
            div_matches += &format!(
                "            ({0}Quantity(v_lhs), {1}Quantity(v_rhs)) => Ok({2}Quantity(v_lhs / v_rhs)),\n",
                lhs, rhs, result
            );
        }

        for caps in mul_with_self_macro_re.captures_iter(content) {
            let lhs = &caps[1];
            let mut result = caps[2].to_string();
            if result == "f64" {
                result = "Float".to_string();
            }
            mul_matches += &format!(
                "                ({0}Quantity(v_lhs), {0}Quantity(v_rhs)) => Ok({1}Quantity(*v_lhs * *v_rhs)),\n",
                lhs, result
            );
        }

        for caps in div_with_self_to_f64_macro_re.captures_iter(content) {
            let lhs = &caps[1];
            div_matches += &format!(
                "            ({0}Quantity(v_lhs), {0}Quantity(v_rhs)) => Ok(FloatQuantity(v_lhs / v_rhs)),\n",
                lhs
            );
        }

        for caps in sqrt_macro_re.captures_iter(content) {
            let result = &caps[2];
            let operand = &caps[1];
            sqrt_matches += &format!(
                "            Quantity::{}Quantity(v) => Ok(Quantity::{}Quantity(v.sqrt())),\n",
                operand, result
            );
        }
        first = false
    }

    let generated = template
        .replace("// __QUANTITY_VARIANTS__", &quantity_variants)
        .replace("// __QUANTITY_TO_VARIANTS__", &quantity_to_variants)
        .replace("// __QUANTITY_FMT_MATCHES__", &quantity_fmt_matches)
        .replace("// __QUANTITY_COMPARISONS__", &quantity_comparisons)
        .replace("// __UNIT_VARIANTS__", &unit_variants)
        .replace("// __TO_QUANTITY_VARIANTS__", &to_quantity_variants)
        .replace("// __QUANTITY_ABS_VARIANTS__", &quantity_abs_variants)
        .replace("// __TO_UNIT_NAME_VARIANTS__", &unit_name_variants)
        .replace("// __EXTRACT_QUANTITY_MATCHES__", &extract_quantity_matches)
        .replace("// __EXTRACT_UNIT_MATCHES__", &extract_unit_matches)
        .replace("// __TO_PYOBJECT_MATCHES__", &to_pyobject_matches)
        .replace("// __MUL_MATCHES__", &mul_matches)
        .replace("// __DIV_MATCHES__", &div_matches)
        .replace("// __BASE_QUANTITY_MATCHES__", &base_quantity_matches)
        .replace("// __ADD_QUANTITY_MATCHES__", &add_matches)
        .replace("// __SUB_QUANTITY_MATCHES__", &sub_matches)
        .replace("// __QUANTITY_SQRTS__", &sqrt_matches);

    let mut f = File::create(dest_path).expect("Could not create output quantities.rs");
    f.write_all(generated.as_bytes())
        .expect("Could not write quantities.rs");
}

fn write_vector_code(
    dest_path: &PathBuf,
    quantity_structs: &Vec<(String, String)>,
    vector_template_path: String,
) {
    let template =
        fs::read_to_string(vector_template_path).expect("Failed to read vector3_py.template.rs");
    let mut raw_interfaces = String::new();
    for struct_data in quantity_structs {
        let struct_name = &struct_data.0;
        let lowercase_name = camel_to_snake(struct_name);
        raw_interfaces += &format!(
            "\n    pub fn from_raw_{}(raw: Vector3<{}>) -> Self {{",
            lowercase_name, struct_name
        );
        raw_interfaces += "\n        Self {";
        raw_interfaces += &format!("\n            data: [Quantity::{}Quantity(raw[0]), Quantity::{}Quantity(raw[1]), Quantity::{}Quantity(raw[2])]", struct_name, struct_name, struct_name);
        raw_interfaces += "\n        }";
        raw_interfaces += "\n    }\n";
        raw_interfaces += &format!(
            "\n    pub fn into_raw_{}(self) -> Result<Vector3<{}>, String> {{",
            lowercase_name, struct_name
        );
        raw_interfaces += &format!("\n        if discriminant(&self.data[0]) != discriminant(&Quantity::{}Quantity({}::zero())) {{", struct_name, struct_name);
        raw_interfaces += "\n            Err(\"Cannot convert Vector3Py into Vector3 with other contained type\".to_string())";
        raw_interfaces += "\n        }";
        raw_interfaces += "\n        else {";
        raw_interfaces += &format!("\n            Ok(Vector3::new([self.data[0].extract_{}()?, self.data[1].extract_{}()?, self.data[2].extract_{}()?]))", lowercase_name, lowercase_name, lowercase_name);
        raw_interfaces += "\n        }";
        raw_interfaces += "\n    }";
    }
    let generated = template.replace("//__RAW_INTERFACE__", &raw_interfaces);
    let mut f = File::create(dest_path).expect("Could not create output vector3_py.rs");
    f.write_all(generated.as_bytes())
        .expect("Could not write vector3_py.rs");
}

fn write_matrix_code(
    dest_path: &PathBuf,
    quantity_structs: &Vec<(String, String)>,
    vector_template_path: String,
) {
    let template =
        fs::read_to_string(vector_template_path).expect("Failed to read matrix3_py.template.rs");
    let mut raw_interfaces = String::new();
    for struct_data in quantity_structs {
        // ToDo: Rewrite raw interface for Matrix3Py
        let struct_name = &struct_data.0;
        let lowercase_name = camel_to_snake(struct_name);
        raw_interfaces += &format!(
            "\n    pub fn from_raw_{}(raw: Matrix3<{}>) -> Self {{",
            lowercase_name, struct_name
        );
        raw_interfaces += "\n        Self {";
        raw_interfaces += &format!("\n            data: [[Quantity::{}Quantity(raw[(0, 0)]), Quantity::{}Quantity(raw[(0, 1)]), Quantity::{}Quantity(raw[(0, 2)])],", struct_name, struct_name, struct_name);
        raw_interfaces += &format!("\n            [Quantity::{}Quantity(raw[(1, 0)]), Quantity::{}Quantity(raw[(1, 1)]), Quantity::{}Quantity(raw[(1, 2)])],", struct_name, struct_name, struct_name);
        raw_interfaces += &format!("\n            [Quantity::{}Quantity(raw[(2, 0)]), Quantity::{}Quantity(raw[(2, 1)]), Quantity::{}Quantity(raw[(2, 2)])]]", struct_name, struct_name, struct_name);
        raw_interfaces += "\n        }";
        raw_interfaces += "\n    }\n";
        raw_interfaces += &format!(
            "\n    pub fn into_raw_{}(self) -> Result<Matrix3<{}>, String> {{",
            lowercase_name, struct_name
        );
        raw_interfaces += &format!("\n        if discriminant(&self.data[0][0]) != discriminant(&Quantity::{}Quantity({}::zero())) {{", struct_name, struct_name);
        raw_interfaces += "\n            Err(\"Cannot convert Matrix3Py into Matrix3 with other contained type\".to_string())";
        raw_interfaces += "\n        }";
        raw_interfaces += "\n        else {";
        raw_interfaces += &format!("\n            Ok(Matrix3::new([[self.data[0][0].extract_{}()?, self.data[0][1].extract_{}()?, self.data[0][2].extract_{}()?],", lowercase_name, lowercase_name, lowercase_name);
        raw_interfaces += &format!("\n            [self.data[1][0].extract_{}()?, self.data[1][1].extract_{}()?, self.data[1][2].extract_{}()?],", lowercase_name, lowercase_name, lowercase_name);
        raw_interfaces += &format!("\n            [self.data[2][0].extract_{}()?, self.data[2][1].extract_{}()?, self.data[2][2].extract_{}()?]]))", lowercase_name, lowercase_name, lowercase_name);
        raw_interfaces += "\n        }";
        raw_interfaces += "\n    }";
    }
    let generated = template.replace("//__RAW_INTERFACE__", &raw_interfaces);
    let mut f = File::create(dest_path).expect("Could not create output matrix3_py.rs");
    f.write_all(generated.as_bytes())
        .expect("Could not write matrix3_py.rs");
}

fn write_module_definition(dest_path: &PathBuf, quantity_structs: &Vec<(String, String)>) {
    let mut module_src = String::from(
        "#[pymodule]\n\
         fn unitforge(_py: Python<'_>, m: Bound<PyModule>) -> PyResult<()> {\n\
         \t m.add_class::<Vector3Py>()?;\n\
         \t m.add_class::<Matrix3Py>()?;\n",
    );
    for (struct_name, _) in quantity_structs {
        module_src.push_str(&format!("\t m.add_class::<{}Unit>()?;\n", struct_name));
        module_src.push_str(&format!("\t m.add_class::<{}>()?;\n", struct_name));
    }
    module_src.push_str("    Ok(())\n}\n");
    fs::write(dest_path, module_src).expect("Could not write python_module_definition.rs")
}
