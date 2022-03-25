from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

import deepxde as dde
from spaces import FinitePowerSeries, FiniteChebyshev, GRF
from system import LTSystem, ODESystem, DRSystem, CVCSystem, ADVDSystem
from utils import merge_values, trim_to_65535, mean_squared_error_outlier, safe_test

# Using the old version of DeepONet 0.11.2

def test_u_lt(nn, system, T, m, model, data, u, fname):
    """Test Legendre transform"""
    sensors = np.linspace(-1, 1, num=m)
    sensor_value = u(sensors)
    s = system.eval_s(sensor_value)
    ns = np.arange(system.npoints_output)[:, None]
    X_test = [np.tile(sensor_value, (system.npoints_output, 1)), ns]
    y_test = s
    if nn != "opnn":
        X_test = merge_values(X_test)
    y_pred = model.predict(data.transform_inputs(X_test))
    np.savetxt("test/u_" + fname, sensor_value)
    np.savetxt("test/s_" + fname, np.hstack((ns, y_test, y_pred)))


def test_u_ode(nn, system, T, m, model, data, u, fname, num=100):
    """Test ODE"""
    sensors = np.linspace(0, T, num=m)[:, None]
    sensor_values = u(sensors)
    x = np.linspace(0, T, num=num)[:, None]
    X_test = [np.tile(sensor_values.T, (num, 1)), x]
    y_test = system.eval_s_func(u, x)
    if nn != "opnn":
        X_test = merge_values(X_test)
    y_pred = model.predict(data.transform_inputs(X_test))
    np.savetxt(fname, np.hstack((x, y_test, y_pred)))
    print("L2relative error:", dde.metrics.l2_relative_error(y_test, y_pred))
    
    # PLOTTING TEST CASES ----------------------------------------------
    # test case 1
    #y_an = 0.5*x**2;
    
    # test case 2
    # analytical needs to be shifted up s.t. y starts from 0
    y_an = -np.cos(2*np.pi * x)/np.pi/2 + 1/2/np.pi
    
    plt.plot(x,y_an,'b')
    plt.plot(x,y_test,'r--')
    
    plt.xlabel('x') 
    plt.ylabel('ytest') 
    plt.title("ode: x vs. ytest")
    plt.legend(['Analytical','DeepONet'])
    plt.show()
    
    plt.plot(x,abs(y_test-y_an))
    plt.xlabel('x')
    plt.ylabel('ytest - y_an')
    plt.title("ode: x vs. error")
    plt.show()
    # -----------------------------------------------------------------


def test_u_dr(nn, system, T, m, model, data, u, fname):
    """Test Diffusion-reaction"""
    sensors = np.linspace(0, 1, num=m)
    sensor_value = u(sensors)
    s = system.eval_s(sensor_value)
    xt = np.array(list(itertools.product(range(m), range(system.Nt))))
    xt = xt * [1 / (m - 1), T / (system.Nt - 1)]
    X_test = [np.tile(sensor_value, (m * system.Nt, 1)), xt]
    y_test = s.reshape([m * system.Nt, 1])
    if nn != "opnn":
        X_test = merge_values(X_test)
    y_pred = model.predict(data.transform_inputs(X_test))
    np.savetxt(fname, np.hstack((xt, y_test, y_pred)))


def test_u_cvc(nn, system, T, m, model, data, u, fname):
    """Test Advection"""
    sensors = np.linspace(0, 1, num=m)
    sensor_value = u(sensors)
    s = system.eval_s(sensor_value)
    xt = np.array(list(itertools.product(range(m), range(system.Nt))))
    xt = xt * [1 / (m - 1), T / (system.Nt - 1)]
    X_test = [np.tile(sensor_value, (m * system.Nt, 1)), xt]
    y_test = s.reshape([m * system.Nt, 1])
    if nn != "opnn":
        X_test = merge_values(X_test)
    y_pred = model.predict(data.transform_inputs(X_test))
    # EDITED BY CHLOE
    #np.savetxt("test/u_" + fname, sensor_value)
    #np.savetxt("test/s_" + fname, np.hstack((xt, y_test, y_pred)))
    
    # PLOTTING TEST CASES ----------------------------------------------    
    plt.plot(xt[:,0],y_pred)
    plt.xlabel('x0') 
    plt.ylabel('ypred') 
    plt.title("Advection: x vs. ypred")
    plt.show()
    # -----------------------------------------------------------------
    
    # plot the solver
    axis = plt.subplot(111)
    plt.imshow(s, cmap="rainbow", vmin=0)
    plt.colorbar()
    xlabel = [format(i, ".1f") for i in np.linspace(0, 1, num=11)]
    ylabel = [format(i, ".1f") for i in np.linspace(0, 1, num=11)]
    axis.set_xticks(range(0, 101, 10))
    axis.set_xticklabels(xlabel)
    axis.set_yticks(range(0, 101, 10))
    axis.set_yticklabels(ylabel)
    axis.set_xlabel("t")
    axis.set_ylabel("x")
    axis.set_title(r"Solver solution", fontdict={"fontsize": 30}, loc="left")
    plt.show()
    
    # plot the actual (chloe)
    x = np.linspace(0, 1, m)
    t = np.linspace(0, 1, m)
    # Case 1
    # V = lambda x: np.sin(2 * np.pi * x)
    # u_true = lambda x, t: V(x - t)
    # u_true = u_true(x[:, None], t)

    # Case 2
    # u_true = lambda x, t: (2 * np.pi * (x - t)) ** 5
    # u_true = u_true(x[:, None], t)
    # axis = plt.subplot(111)
    # plt.imshow(u_true, cmap="rainbow", vmin=0)
    # plt.colorbar()
    # xlabel = [format(i, ".1f") for i in np.linspace(0, 1, num=11)]
    # ylabel = [format(i, ".1f") for i in np.linspace(0, 1, num=11)]
    # axis.set_xticks(range(0, 101, 10))
    # axis.set_xticklabels(xlabel)
    # axis.set_yticks(range(0, 101, 10))
    # axis.set_yticklabels(ylabel)
    # axis.set_xlabel("t")
    # axis.set_ylabel("x")
    # axis.set_title(r"Actual solution", fontdict={"fontsize": 30}, loc="left")
    # plt.show()

    # plot the error (original)
    # error = abs(s - u_true)
    # axis = plt.subplot(111)
    # plt.imshow(error, cmap="rainbow", vmin=0)
    # plt.colorbar()
    # xlabel = [format(i, ".1f") for i in np.linspace(0, 1, num=11)]
    # ylabel = [format(i, ".1f") for i in np.linspace(0, 1, num=11)]
    # axis.set_xticks(range(0, 101, 10))
    # axis.set_xticklabels(xlabel)
    # axis.set_yticks(range(0, 101, 10))
    # axis.set_yticklabels(ylabel)
    # axis.set_xlabel("t")
    # axis.set_ylabel("x")
    # axis.set_title(r"Error", fontdict={"fontsize": 30}, loc="left")
    # plt.show()



def test_u_advd(nn, system, T, m, model, data, u, fname):
    """Test Advection-diffusion"""
    sensors = np.linspace(0, 1, num=m)
    sensor_value = u(sensors)
    s = system.eval_s(sensor_value)
    xt = np.array(list(itertools.product(range(m), range(system.Nt))))
    xt = xt * [1 / (m - 1), T / (system.Nt - 1)]
    X_test = [np.tile(sensor_value, (m * system.Nt, 1)), xt]
    y_test = s.reshape([m * system.Nt, 1])
    if nn != "opnn":
        X_test = merge_values(X_test)
    y_pred = model.predict(data.transform_inputs(X_test))
    np.savetxt("test/u_" + fname, sensor_value)
    np.savetxt("test/s_" + fname, np.hstack((xt, y_test, y_pred)))


def lt_system(npoints_output):
    """Legendre transform"""
    return LTSystem(npoints_output)


def ode_system(T):
    """ODE"""

    def g(s, u, x):
        # Antiderivative
        return u
        # Nonlinear ODE
        # return -s**2 + u
        # Gravity pendulum
        # k = 1
        # return [s[1], - k * np.sin(s[0]) + u]

    s0 = [0]
    # s0 = [0, 0]  # Gravity pendulum
    return ODESystem(g, s0, T)


def dr_system(T, npoints_output):
    """Diffusion-reaction"""
    D = 0.01
    k = 0.01
    Nt = 100
    return DRSystem(D, k, T, Nt, npoints_output)


def cvc_system(T, npoints_output):
    """Advection"""
    f = None
    g = None
    Nt = 100
    return CVCSystem(f, g, T, Nt, npoints_output)


def advd_system(T, npoints_output):
    """Advection-diffusion"""
    f = None
    g = None
    Nt = 100
    return ADVDSystem(f, g, T, Nt, npoints_output)


def run(problem, system, space, T, m, nn, net, lr, epochs, num_train, num_test):
    # space_test = GRF(1, length_scale=0.1, N=1000, interp="cubic")

    X_train, y_train = system.gen_operator_data(space, m, num_train)
    X_test, y_test = system.gen_operator_data(space, m, num_test)
    if nn != "opnn":
        X_train = merge_values(X_train)
        X_test = merge_values(X_test)

    # np.savez_compressed("train.npz", X_train0=X_train[0], X_train1=X_train[1], y_train=y_train)
    # np.savez_compressed("test.npz", X_test0=X_test[0], X_test1=X_test[1], y_test=y_test)
    # return

    # d = np.load("train.npz")
    # X_train, y_train = (d["X_train0"], d["X_train1"]), d["y_train"]
    # d = np.load("test.npz")
    # X_test, y_test = (d["X_test0"], d["X_test1"]), d["y_test"]

    X_test_trim = trim_to_65535(X_test)[0]
    y_test_trim = trim_to_65535(y_test)[0]
    if nn == "opnn":
        data = dde.data.OpDataSet(
            X_train=X_train, y_train=y_train, X_test=X_test_trim, y_test=y_test_trim
        )
    else:
        data = dde.data.DataSet(
            X_train=X_train, y_train=y_train, X_test=X_test_trim, y_test=y_test_trim
        )

    model = dde.Model(data, net)
    model.compile("adam", lr=lr, metrics=[mean_squared_error_outlier])
    checker = dde.callbacks.ModelCheckpoint(
        "model/model.ckpt", save_better_only=True, period=1000
    )
    losshistory, train_state = model.train(epochs=epochs, callbacks=[checker])
    # print("# Parameters:", np.sum([np.prod(v.get_shape().as_list()) for v in tf.trainable_variables()]))
    print("# Parameters:", np.sum([np.prod(v.get_shape().as_list()) for v in tf.compat.v1.trainable_variables()]))

    dde.saveplot(losshistory, train_state, issave=True, isplot=True)

    model.restore("model/model.ckpt-" + str(train_state.best_step), verbose=1)
    
    print("Rows of X_train = " + str(len(X_train)))
    print("Columns of X_train = " + str(len(X_train[0])))
    print("Rows of y_train = " + str(len(y_train)))
    print("Columns of y_train = " + str(len(y_train[0])))
    
    
    # PLOTTING TRAINED DATA ----------------------------
    if problem == "ode":
        x = np.linspace(0, T, num=1000)[:, None]
        plt.plot(x,y_train)
        plt.xlabel('x') 
        plt.ylabel('ytrain') 
        plt.title("ode: x vs. ytrain")
        plt.show()
    # --------------------------------------------------
    
    safe_test(model, data, X_test, y_test)

    tests = [
        #(lambda x: x, "x.dat"),
        #(lambda x: np.sin(np.pi * x), "sinx.dat"),
        (lambda x: np.sin(2 * np.pi * x), "sin2x.dat"),
        #(lambda x: x * np.sin(2 * np.pi * x), "xsin2x.dat"),
    ]
    for u, fname in tests:
        if problem == "lt":
            test_u_lt(nn, system, T, m, model, data, u, fname)
        elif problem == "ode":
            test_u_ode(nn, system, T, m, model, data, u, fname)
        elif problem == "dr":
            test_u_dr(nn, system, T, m, model, data, u, fname)
        elif problem == "cvc":
            test_u_cvc(nn, system, T, m, model, data, u, fname)
        elif problem == "advd":
            test_u_advd(nn, system, T, m, model, data, u, fname)

    if problem == "lt":
        features = space.random(10)
        sensors = np.linspace(0, 2, num=m)[:, None]
        u = space.eval_u(features, sensors)
        for i in range(u.shape[0]):
            test_u_lt(nn, system, T, m, model, data, lambda x: u[i], str(i) + ".dat")

    if problem == "cvc":
        features = space.random(10)
        sensors = np.linspace(0, 1, num=m)[:, None]
        # Case I Input: V(sin^2(pi*x))
        # u = space.eval_u(features, np.sin(np.pi * sensors) ** 2)
        # Case II Input: x*V(x)
        u = sensors.T * space.eval_u(features, sensors)
        # Case III/IV Input: V(x)
        # u = space.eval_u(features, sensors)
        for i in range(u.shape[0]):
            test_u_cvc(nn, system, T, m, model, data, lambda x: u[i], str(i) + ".dat")

    if problem == "advd":
        features = space.random(10)
        sensors = np.linspace(0, 1, num=m)[:, None]
        u = space.eval_u(features, np.sin(np.pi * sensors) ** 2)
        for i in range(u.shape[0]):
            test_u_advd(nn, system, T, m, model, data, lambda x: u[i], str(i) + ".dat")



def main():
    # Problems:
    # - "lt": Legendre transform
    # - "ode": Antiderivative, Nonlinear ODE, Gravity pendulum
    # - "dr": Diffusion-reaction
    # - "cvc": Advection
    # - "advd": Advection-diffusion
    problem = "ode"
    T = 1
    if problem == "lt":
        npoints_output = 20
        system = lt_system(npoints_output)
    elif problem == "ode":
        system = ode_system(T)
    elif problem == "dr":
        npoints_output = 100
        system = dr_system(T, npoints_output)
    elif problem == "cvc":
        npoints_output = 100
        system = cvc_system(T, npoints_output)
    elif problem == "advd":
        npoints_output = 100
        system = advd_system(T, npoints_output)

    # Function space
    # space = FinitePowerSeries(N=100, M=1)
    # space = FiniteChebyshev(N=20, M=1)
    # space = GRF(2, length_scale=0.2, N=2000, interp="cubic")  # "lt"
    space = GRF(1, length_scale=0.2, N=1000, interp="cubic")
    # space = GRF(T, length_scale=0.2, N=1000 * T, interp="cubic")

    # Hyperparameters
    m = 100
    num_train = 1000 # 10000
    num_test = 100 # 100000, proof: test > train
    lr = 0.001
    epochs = 1000 # 50000 originally, how many times iterate model

    # Network
    nn = "opnn"
    activation = "relu"
    initializer = "Glorot normal"  # "He normal" or "Glorot normal"
    dim_x = 1 if problem in ["ode", "lt"] else 2
    if nn == "opnn":
        net = dde.maps.OpNN(
            [m, 40, 40],
            [dim_x, 40, 40],
            activation,
            initializer,
            use_bias=True,
            stacked=False,
        )
    elif nn == "fnn":
        net = dde.maps.FNN([m + dim_x] + [100] * 2 + [1], activation, initializer)
    elif nn == "resnet":
        net = dde.maps.ResNet(m + dim_x, 1, 128, 2, activation, initializer)

    run(problem, system, space, T, m, nn, net, lr, epochs, num_train, num_test)
    


if __name__ == "__main__":
    main()
