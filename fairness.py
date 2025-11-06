import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss
)
from xgboost import XGBClassifier
import joblib
from sklearn.calibration import calibration_curve

print("Cargando datos preprocesados...")
X_train = pd.read_csv("X_train.csv")
y_train = pd.read_csv("y_train.csv").squeeze()
X_test = pd.read_csv("X_test.csv")
y_test = pd.read_csv("y_test.csv").squeeze()
feature_names = list(X_train.columns)

print(f"Datos cargados: {X_train.shape[0]} train / {X_test.shape[0]} test")
print(f"   Features: {len(feature_names)} columnas")

print("\nGenerando pesos de muestra para reducir desigualdad...")

try:
    df_train_full = pd.read_csv('df_train_ready.csv')
    
    if len(df_train_full) != len(X_train):
        print("   Advertencia: df_train_ready.csv y X_train.csv tienen longitudes diferentes.")
        print("   Alineando por índice...")
        df_train_full = df_train_full.loc[X_train.index]
    else:
        df_train_full.index = X_train.index

    if 'RIDRETH3' in df_train_full.columns:
        X_train_fairness = X_train.copy()
        X_train_fairness['RIDRETH3'] = df_train_full['RIDRETH3']
        
        group_counts = X_train_fairness['RIDRETH3'].value_counts()
        total_samples = len(X_train_fairness)
        
        n_classes = len(group_counts)
        weights = total_samples / (n_classes * group_counts)
        
        sample_weights = X_train_fairness['RIDRETH3'].map(weights)
        
        sample_weights = sample_weights.fillna(1.0)
        
        print(f"   Pesos creados basados en 'RIDRETH3'.")
        print("   Pesos por grupo (ejemplo):")
        print(weights.sort_index())
    else:
        print("   Columna 'RIDRETH3' no encontrada en df_train_ready.csv. Usando pesos uniformes.")
        sample_weights = np.ones(len(X_train))

except FileNotFoundError:
    print("   'df_train_ready.csv' no encontrado. Usando pesos uniformes.")
    sample_weights = np.ones(len(X_train))

print("\n=== Baseline: Logistic Regression (con pesos de equidad) ===")

pipeline_lr = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(
        random_state=42, max_iter=1000, class_weight='balanced'
    ))
])

print("Entrenando Logistic Regression...")

pipeline_lr.fit(X_train, y_train, classifier__sample_weight=sample_weights)

print("   ...Entrenamiento LR completado.")

y_pred_proba_lr = pipeline_lr.predict_proba(X_test)[:, 1]

auroc_lr = roc_auc_score(y_test, y_pred_proba_lr)
auprc_lr = average_precision_score(y_test, y_pred_proba_lr)
brier_lr = brier_score_loss(y_test, y_pred_proba_lr)

print(f"\nBASELINE - Logistic Regression:")
print(f"   AUROC: {auroc_lr:.4f}")
print(f"   AUPRC: {auprc_lr:.4f}")
print(f"   Brier Score: {brier_lr:.4f}")

joblib.dump(pipeline_lr, 'model_baseline_lr.pkl')
print("Modelo guardado: model_baseline_lr.pkl")

print("\n=== Modelo Avanzado: XGBoost (con pesos de equidad) ===")

imputer = SimpleImputer(strategy='median')
X_train_imp = pd.DataFrame(
    imputer.fit_transform(X_train),
    columns=X_train.columns,
    index=X_train.index
)
X_test_imp = pd.DataFrame(
    imputer.transform(X_test),
    columns=X_test.columns,
    index=X_test.index
)

pos_count = (y_train == 1).sum()
neg_count = (y_train == 0).sum()
if pos_count == 0:
    print("ADVERTENCIA: No hay casos positivos.")
    scale_pos_weight = 1.0
else:
    scale_pos_weight = neg_count / pos_count

print(f"   Desbalance (clases): {neg_count:,} negativos / {pos_count:,} positivos")
print(f"   scale_pos_weight: {scale_pos_weight:.2f}")

model_xgb = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    eval_metric='logloss'
)

print("Entrenando XGBoost...")

model_xgb.fit(
    X_train_imp, 
    y_train, 
    sample_weight=sample_weights,
    eval_set=[(X_test_imp, y_test)], 
    verbose=False
)
print("   ...Entrenamiento XGBoost completado.")

y_pred_proba_xgb = model_xgb.predict_proba(X_test_imp)[:, 1]

auroc_xgb = roc_auc_score(y_test, y_pred_proba_xgb)
auprc_xgb = average_precision_score(y_test, y_pred_proba_xgb)
brier_xgb = brier_score_loss(y_test, y_pred_proba_xgb)

print(f"\nXGBoost:")
print(f"   AUROC: {auroc_xgb:.4f} {'✓' if auroc_xgb >= 0.80 else ''}")
print(f"   AUPRC: {auprc_xgb:.4f}")
print(f"   Brier Score: {brier_xgb:.4f} {'✓' if brier_xgb <= 0.12 else ''}")

feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': model_xgb.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Features:")
print(feature_importance.head(10).to_string(index=False))

joblib.dump(model_xgb, 'model_xgboost.pkl')
joblib.dump(imputer, 'imputer.pkl')
joblib.dump(feature_names, 'feature_names.pkl')
print("Modelo guardado: model_xgboost.pkl")

print("\n=== Curvas de calibración ===")

prob_true_lr, prob_pred_lr = calibration_curve(y_test, y_pred_proba_lr, n_bins=10)
prob_true_xgb, prob_pred_xgb = calibration_curve(y_test, y_pred_proba_xgb, n_bins=10)

fig, ax = plt.subplots(figsize=(8, 7))
ax.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
ax.plot(prob_pred_lr, prob_true_lr, 'o-', label=f'Logistic Regression (Brier={brier_lr:.4f})')
ax.plot(prob_pred_xgb, prob_true_xgb, 's-', label=f'XGBoost (Brier={brier_xgb:.4f})')
ax.set_xlabel('Mean predicted probability', fontsize=12)
ax.set_ylabel('Fraction of positives', fontsize=12)
ax.set_title('Calibration Curves', fontsize=14, fontweight='bold')
ax.legend(loc='upper left')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('calibration_curves.png', dpi=300, bbox_inches='tight')
plt.show()

print("Curvas de calibración guardadas en calibration_curves.png")

print("\nProceso de entrenamiento con rebalanceo de equidad completado.")