![text](https://pouch.jumpshare.com/preview/-1bim1AldefPqJAQ8tSYVMv4QCpJQ01cjvxm3Hsiqvj8El3FZhJFamBeqytuK5aClqfxZB9c_M6FK4pY8ecv7ePIslOnu4vxog90qafZ7dg)

# NoTorch 🕯

**A pure Python, educational machine learning library — built from scratch.**

**NoTorch** is a learning-focused machine learning and deep learning library that re-implements popular models using only core Python (and `pandas` for data handling). Inspired by the design of `scikit-learn` and `PyTorch`, NoTorch offers a simple and consistent API while prioritizing **readability**, **clarity**, and **educational value** over performance or production use.

This project is being developed as part of a personal journey to deeply understand how machine learning works — and to help others learn by example. Whether you're a student, a hobbyist, or just curious about what happens *under the hood* of your favorite ML libraries, NoTorch is here to make complex concepts transparent and approachable.

---

## 🔍 Project Goals

* ✅ Build core ML and DL models **from scratch** in pure Python
* ✅ Keep the code **readable**, **modular**, and **well-documented**
* ✅ Mimic the familiar APIs of `sklearn` and `torch` for a smoother learning curve
* ✅ Prioritize **educational clarity** over performance or abstraction
* ✅ Share the learning journey with the community

---

## ✅ Implemented Models

### Classical Machine Learning

* [x] **K-Nearest Neighbors (KNN)**
* [ ] **Decision Tree**
* [ ] **Random Forest**
* [ ] **Naive Bayes**
* [ ] **Linear Regression**
* [ ] **Logistic Regression**
* [ ] **Support Vector Machine (SVM)**

### Neural Networks (Coming Soon)

* [ ] **Basic Feedforward Neural Network**
* [ ] **Manual Backpropagation Engine**
* [ ] **Custom Autograd System (Experimental)**
* [ ] **Convolutional Neural Networks (CNNs)**
* [ ] **Recurrent Neural Networks (RNNs)**
* [ ] **Long Short-Term Memory (LSTM)**

---

## 🛠 Example Usage
### KNN Model
```python
from NoTorch.KNN import KNN

model = KNN(n_neighbors=1)
model.fit(X_train, y_train)

print(model.predict(X_test))
```

---

<!-- ## 📚 Documentation

Check out our full documentation, examples, and development notes at:
👉 [Project Docs](https://your-docs-url-here.com)

--- -->

## 🚧 This Project is Under Active Development

NoTorch is a work-in-progress, built step-by-step with the intent to **learn by building**. Contributions, ideas, and educational feedback are very welcome!


