# main.py

from .core import *  
from .config_loader import cargar_json_usuario
from pathlib import Path
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')

def VacancyAnalysis():
    
    base = "outputs"
    for sub in ("csv", "dump", "json"):
        os.makedirs(os.path.join(base, sub), exist_ok=True)

    
    processor = TrainingProcessor()
    processor.run()

    
    CONFIG = cargar_json_usuario()
    
    if "CONFIG" not in CONFIG or not isinstance(CONFIG["CONFIG"], list) or len(CONFIG["CONFIG"]) == 0:
        raise ValueError("input_params.json debe contener una lista 'CONFIG' con al menos un objeto.")

    configuracion = CONFIG["CONFIG"][0]
    defect_file = configuracion['defect']

    cs_out_dir = Path("inputs")
    cs_generator = CrystalStructureGenerator(configuracion, cs_out_dir)
    dump_path = cs_generator.generate()
    print(f"Estructura relajada generada en: {dump_path}")

    processor = ClusterProcessor(defect_file)
    processor.run()
    separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
    separator.run()

    # 3. Procesar dumps críticos
    clave_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
    for archivo in clave_criticos:
        try:
            dump_proc = ClusterDumpProcessor(archivo, decimals=5)
            dump_proc.load_data()
            dump_proc.process_clusters()
            dump_proc.export_updated_file(f"{archivo}_actualizado.txt")
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

    # 4. Subdivisión iterativa
    lista_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
    for archivo in lista_criticos:
        machine_proc = ClusterProcessorMachine(archivo, configuracion['cluster tolerance'], configuracion['iteraciones_clusterig'])
        machine_proc.process_clusters()
        machine_proc.export_updated_file()

    # 5. Separar archivos finales vs críticos
    separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
    separator.run()

    # 6. Generar nuevos dumps por cluster
    export_list = ExportClusterList("outputs/json/key_archivos.json")
    export_list.process_files()

    # 7. Calcular superficies de dump
    surf_proc = SurfaceProcessor(configuracion)
    surf_proc.process_all_files()
    surf_proc.export_results()



    #7' metodologia HSM
    key_file = resolve_input_params_path('outputs/json/key_archivos.json')
    with open(key_file, 'r', encoding='utf-8') as jf:
        config = json.load(jf)

    cluster_files = config.get('clusters_final', [])
    ref_file = 'inputs/relax_structure.dump'  # tu red de referencia

    for cluster_path in cluster_files:
        # Nombre base para salida
        base = os.path.splitext(os.path.basename(cluster_path))[0]
        out_dump = f'outputs/dump/{base}_inside.dump'

        # Procesar cada dump
        proc = HSM(cluster_path)
        proc.read_and_translate()
        expr = proc.compute_hull_expression(strict=True)
        #print(f"Expresión para {cluster_path}:\n{expr}\n")
        proc.apply_to_reference(ref_file, out_dump)
        #print(f"→ Dump filtrado escrito en: {out_dump}\n")









    # 8. Predicción con modelos
    params = cargar_json_usuario()

    predictor_cols = params.get("PREDICTOR_COLUMNS", None)
    if predictor_cols is None or not isinstance(predictor_cols, list) or len(predictor_cols) == 0:
        raise KeyError("input_params.json debe contener 'PREDICTOR_COLUMNS' (lista no vacía) en el nivel raíz.")

    rf_predictor = VacancyPredictorRF(
        json_path="outputs/json/training_data.json",
        predictor_columns=predictor_cols
    )
    xgb_predictor = XGBoostVacancyPredictor(
        training_data_path="outputs/json/training_data.json",
        model_path="outputs/json/xgboost_model.json",
        predictor_columns=predictor_cols
    )
    rf_predictor_graph = VacancyPredictorRF(
        json_path="outputs/json/training_graph.json",
        predictor_columns=predictor_cols
    )
    xgb_predictor_graph = XGBoostVacancyPredictor(
        training_data_path="outputs/json/training_graph.json",
        model_path="outputs/json/xgboost_model.json",
        predictor_columns=predictor_cols
    )

    csv_path = os.path.join("outputs", "csv", "defect_data.csv")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV en: {csv_path}")

    df = pd.read_csv(csv_path)

    print(f"\\********** Predicciones para defecto {defect_file} usando {csv_path} *************")
    for idx, row in df.iterrows():
        try:
            features = {col: row[col] for col in predictor_cols}
        except KeyError as e:
            raise KeyError(
                f"La columna {e} no existe en el CSV. Columnas disponibles: {list(df.columns)}"
            )

        vac_pred_rf = rf_predictor.predict_vacancies(**features)
        sample_features = [[features[col] for col in predictor_cols]]
        vac_pred_xgb = xgb_predictor.predict(sample_features)

        print(f"Fila {idx} → features: {features}")
        print(f"  • Predicción RF (vacancias): {vac_pred_rf}")
        print(f"  • Predicción XGBoost (vacancias): {vac_pred_xgb}\n")
        #AHORA PARA GRAPH TRAINING

        vac_pred_rf_graph = rf_predictor_graph.predict_vacancies(**features)
        sample_features_graph = [[features[col] for col in predictor_cols]]
        vac_pred_xgb_graph = xgb_predictor_graph.predict(sample_features)

        print(f"Fila {idx} → features: {features}")
        print(f"  • Predicción RF GRAPH (vacancias): {vac_pred_rf_graph}")
        print(f"  • Predicción XGBoost GRAPH (vacancias): {vac_pred_xgb_graph}\n")

        json_input = "outputs/json/key_archivos.json"
        output_csv_path = "outputs/csv/finger_defect_data.csv"
        exporter = JSONFeatureExporterFinger(json_input, output_csv_path)
        exporter.export()

        winner_finder = WinnerFinger(
            defect_csv=Path("outputs/csv/finger_defect_data.csv"),
            normal_csv=Path("outputs/csv/finger_data.csv"),
            output_csv=Path("outputs/csv/finger_winner_data.csv"),
            id_col="file_name"
        )
        winner_finder.run()

    defect_csv = Path('outputs/csv/defect_data.csv')
    finger_csv = Path('outputs/csv/finger_winner_data.csv')
    output_csv = Path('outputs/csv/defect_data.csv')

    defect_df = pd.read_csv(defect_csv)
    finger_df = pd.read_csv(finger_csv)
    finger_df = finger_df[['defect_file', 'fingerprint']]
    defect_df['file_name'] = defect_df['archivo'].apply(lambda p: Path(p).name)

    enriched = defect_df.merge(
        finger_df,
        how='left',
        left_on='file_name',
        right_on='defect_file'
    )

    enriched = enriched.drop(columns=['file_name', 'defect_file'])
    enriched.to_csv(output_csv, index=False)
    print(f'CSV enriquecido guardado en: {output_csv}')

if __name__ == "__main__":
    VacancyAnalysis()
    print("Script ejecutado correctamente.")



