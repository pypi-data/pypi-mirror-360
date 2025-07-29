class_ = "Methylation class"
analysis.set_betas()
X = analysis.betas_all
X_all = analysis.betas_all
# X = analysis.betas_all.iloc[:,:25000]
y = analysis.idat_handler.samples_annotated[class_]

# Split data into training and testing sets (optional, if needed)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42
)

# Step 1: Train a Random Forest Classifier on the entire dataset
best_parms = {
    "n_estimators": 1400,
    "min_samples_split": 2,
    "min_samples_leaf": 2,
    "max_features": "sqrt",
    "max_depth": 70,
    "bootstrap": False,
    "random_state": 42,
    "n_jobs": -1,
}
parms = {
    "n_estimators": 300,
    "random_state": 42,
    "n_jobs": -1,
}
rf = RandomForestClassifier(**parms)
rf.fit(X_train, y_train)

param_grid = {"n_estimators": randint(50, 500), "max_depth": randint(1, 20)}
rf = RandomForestClassifier()
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_grid,
    n_iter=100,
    cv=3,
    scoring="accuracy",
    n_jobs=-1,
    verbose=4,
    random_state=42,
)

random_search.fit(X_train, y_train)

rbf_svc = SVC(kernel="rbf")
rbf_svc.fit(X_train, y_train)
y_pred = rbf_svc.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy:", accuracy)


# Calculate and print accuracy
y_pred = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy:", accuracy)


# Step 2: Get Feature Importances
feature_importances = rf.feature_importances_

# Step 3: Select Top 10,000 Features
# Get indices of features sorted by importance (descending order)
top_features_indices = np.argsort(feature_importances)[-10000:]

# Select the top 10,000 features from X_train and X_test
X_train_selected = X_train[:, top_features_indices]
X_test_selected = X_test[:, top_features_indices]

# The data (X_train_selected and X_test_selected) now only contain the top 10,000 features


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

param_grid = {
    "n_estimators": [300, 500, 1000],
    "max_depth": [None, 10, 20, 30],
    "max_features": ["sqrt", "log2"],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}
rf = RandomForestClassifier(random_state=42, n_jobs=-1)

grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=3,
    scoring="accuracy",
    n_jobs=-1,
    verbose=4,
)
grid_search.fit(X_train, y_train)
best_rf = grid_search.best_estimator_
print("Best Hyperparameters:", grid_search.best_params_)
y_pred = best_rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy:", accuracy)


random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_grid,
    n_iter=100,
    cv=3,
    scoring="accuracy",
    n_jobs=-1,
    verbose=4,
    random_state=42,
)
random_search.fit(X_train, y_train)
best_rf = random_search.best_estimator_
print("Best Hyperparameters:", random_search.best_params_)
y_pred = best_rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy:", accuracy)


n_estimators = [int(x) for x in np.linspace(start=200, stop=2000, num=10)]
max_features = ["auto", "sqrt"]
max_depth = [int(x) for x in np.linspace(10, 110, num=11)]
max_depth.append(None)
min_samples_split = [2, 5, 10]
min_samples_leaf = [1, 2, 4]
bootstrap = [True, False]  # Create the random grid
random_grid = {
    "n_estimators": n_estimators,
    "max_features": max_features,
    "max_depth": max_depth,
    "min_samples_split": min_samples_split,
    "min_samples_leaf": min_samples_leaf,
    "bootstrap": bootstrap,
}
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=random_grid,
    n_iter=300,
    cv=3,
    n_jobs=-1,
    verbose=2,
    random_state=42,
)
random_search.fit(X_train, y_train)
best_rf = random_search.best_estimator_
print("Best Hyperparameters:", random_search.best_params_)
y_pred = best_rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy:", accuracy)


# Assuming X and y are already loaded as shown in your input

# Standardize the data (important for PCA and many classifiers)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_new = SelectKBest(f_classif, k=10000).fit_transform(X_all, y)
X_new.shape

# Apply PCA for dimensionality reduction
pca = PCA(n_components=50)  # Adjust number of components as needed
X_pca = pca.fit_transform(X_scaled)
X_pca = pca.fit_transform(X)

X_umap = umap.UMAP(**analysis.umap_parms, n_components=20).fit_transform(X)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_pca, y, test_size=0.3, random_state=42
)

# Define classifiers to compare
classifiers = {
    # "AdaBoost": AdaBoostClassifier(n_estimators=100, random_state=42),
    "Extra Trees": ExtraTreesClassifier(n_estimators=300, random_state=42),
    # "Gradient Boosting": GradientBoostingClassifier( n_estimators=100, random_state=42),
    # "Hist Gradient Boosting": HistGradientBoostingClassifier( max_iter=100, random_state=42),
    # "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
    # "LightGBM": LGBMClassifier(random_state=42),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "_Logistic Regression": LogisticRegression(C= 100, penalty= 'l1', solver= 'liblinear'),
    # "MLP (Neural Network)": MLPClassifier( hidden_layer_sizes=(100,), max_iter=1000, random_state=42),
    # "Naive Bayes": GaussianNB(),
    "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42),
    "SVM": SVC(kernel="rbf", probability=True, random_state=42),
    "LinearSVC": LinearSVC(random_state=42),
    # "XGBoost": XGBClassifier( use_label_encoder=False, eval_metric="logloss", random_state=42),
}

# Dictionary to store cross-validation results
results = {}

for name, clf in classifiers.items():
    # scores = cross_val_score(clf, X_umap, y, cv=10, scoring='accuracy')
    # scores = cross_val_score(clf, X_pca, y, cv=10, scoring='accuracy')
    scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy", n_jobs=2)
    # scores = cross_val_score(clf, X_new, y, cv=5, scoring="accuracy", n_jobs=2)
    results[name] = np.mean(scores)
    print(f"{name} Accuracy: {np.mean(scores):.4f} ± {np.std(scores):.4f}")


# Find the best classifier
best_clf_name = max(results, key=results.get)
print(
    f"\nBest Classifier: {best_clf_name} with Accuracy: {results[best_clf_name]:.4f}"
)

# Train and evaluate the best classifier on the test set
best_clf = classifiers[best_clf_name]
pipeline = Pipeline(
    [
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=50)),
        ("clf", best_clf),
    ]
)
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy of {best_clf_name}: {accuracy:.4f}")


from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression

param_grid = {
    "penalty": ["l1", "l2", "elasticnet"],
    "C": [0.01, 0.1, 1, 10, 100],
    "solver": [
        "lbfgs",
        "l2",
        "liblinear",
        "newton-cg",
        "newton-cholesky",
        "sag",
        "saga",
    ],
    "l1_ratio": [0, 0.5, 1],
}
param_grid = {
    "penalty": ["l1"],
    "C": range(100),
    "solver": [
        "liblinear",
    ],
}
grid_search = GridSearchCV(
    LogisticRegression(max_iter=100, random_state=42),
    param_grid,
    cv=3,
    scoring="accuracy",
    verbose=5,
    n_jobs=3,
)
grid_search.fit(X_train, y_train)
best_params = grid_search.best_params_
best_score = grid_search.best_score_
print(f"Best Parameters: {best_params}")
print(f"Best Cross-Validation Accuracy: {best_score:.4f}")
best_logreg = grid_search.best_estimator_
best_logreg.fit(X_train, y_train)
y_pred = best_logreg.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy with Tuned Logistic Regression: {accuracy:.4f}")





