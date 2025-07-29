from pytest import approx, mark
from geometry.quaternion import Quaternion, Q0
from geometry.point import Point, PX, PY, PZ, P0
from geometry import Euler, Euldeg
from geometry.checks import assert_almost_equal
import pandas as pd
import numpy as np

import quaternion

def test_init():
    data = np.random.random((500,4))
    qs = Quaternion(data)
    np.testing.assert_array_equal(data, qs.data)


def test_mul():
    q1 = Quaternion(np.random.random((2, 4))).norm()
    q2 = Quaternion(np.random.random((2, 4))).norm()

    def npcheck(q1, q2):
        res = np.quaternion(*q1.data[0]) * np.quaternion(*q2.data[0])
        return np.array([res.w, res.x, res.y, res.z])

    check = q1 * q2
    check_npy=np.array([
        npcheck(_1,_2) for _1, _2 in zip(q1, q2)
    ])
    
    
    np.testing.assert_array_almost_equal(
        check.data,
        check_npy,
        err_msg="failed to do Quaternions * Quaternions"
    )


def test_from_euler_unwrap():    
    q = Q0(10).rotate(PZ()*np.radians(np.linspace(0,360, 10)))
    np.testing.assert_array_almost_equal(
        Quaternion.from_euler(q.to_euler()).diff(1).data, 
        q.diff(1).data
    )



def test_norm():
    qarr = Quaternion(np.random.random( (2,4)))

    def npcheck(q1):
        res = np.quaternion(*q1.data[0]).normalized()
        return np.array([res.w, res.x, res.y, res.z])    

    earr = [npcheck(q) for q in qarr]
    np.testing.assert_array_almost_equal(
        qarr.norm().data,
        earr
    )

def test_conjugate():

    qarr = Quaternion(np.random.random((6, 4))).norm()


    def npcheck(q1):
        res = np.quaternion(*q1.data[0]).conjugate()
        return np.array([res.w, res.x, res.y, res.z])

    earr = np.array([npcheck(q) for q in qarr])
    np.testing.assert_array_almost_equal(
        qarr.conjugate().data,
        earr
    )

def test_inverse():

    q = Quaternion(1,0,0,0)
    assert q.norm() == Quaternion(1,0,0,0)


    def npcheck(q1):
        res = np.quaternion(*q1.data[0]).inverse()
        return np.array([res.w, res.x, res.y, res.z])

    qarr = Quaternion(np.random.random((2, 4))).norm()

    earr = [npcheck(q) for q in qarr]

    np.testing.assert_array_almost_equal(qarr.inverse().data,earr)

def test_body_diff():
    qs = Quaternion.zero(100)
    qs = qs.body_rotate(Point.X(1, 100) * np.linspace(0,np.pi, 100))
    dt = np.ones(100)
    dq = qs.body_diff(dt)
    np.testing.assert_array_almost_equal(
        dq.data,
        Point.X(np.pi/100, 100).data
    )

def test_tp_2():
    np.testing.assert_array_equal(
        Quaternion(0.1, 0, 0,0).norm().transform_point(Point(1,0,0)).data,
        Point(1,0,0).data 
    )



def test_rotate():
    q = Quaternion.from_euler(P0())
    qdot = q.rotate(Point(0, 0, np.radians(5)))
    assert qdot.transform_point(PX()).y == approx(np.sin(np.radians(5)))

def test_body_rotate():
    q = Quaternion.from_euler(Point(0, 0, np.pi / 2))
    qdot = q.body_rotate(Point(np.radians(5), 0, 0))

    assert qdot.transform_point(Point(0, 1, 0)).z == np.sin(np.radians(5))

def test_body_rotate_zero():
    qinit = Quaternion.from_euler(Point(0, 0, 0))
    qdot = qinit.body_rotate(Point(0, 0, 0))

    assert qinit == qdot
#    np.testing.assert_array_equal(list(qinit), list(qdot))


def test_to_from_axis_angle():
    points = Point(np.random.random((100, 3)))
    tqs = Quaternion.from_axis_angle(points)
    tps = tqs.to_axis_angle()

    np.testing.assert_array_almost_equal(
        points.data,
        tps.data
    )

def test_to_axis_angle():
    q1 = Quaternion.from_euler(PZ(np.pi/4))
    
    assert_almost_equal( q1.to_axis_angle(), PZ(np.pi/4))



def test_axis_rates():
    q    = Quaternion.from_euler(Point(0.0, 0.0, np.pi/2))
    qdot = Quaternion.from_euler(Point(np.radians(5), 0.0, np.pi/2))

    rates = Quaternion.axis_rates(q, qdot)

    np.testing.assert_almost_equal(np.degrees(rates.data), Point(0,5,0).data)

def test_body_axis_rates():
    q = Quaternion.from_euler(Point(0, 0, np.pi / 2))
    qdot = Quaternion.from_euler(Point(np.radians(5), 0, np.pi / 2))

    rates = Quaternion.body_axis_rates(q, qdot)
    np.testing.assert_almost_equal(np.degrees(rates.data), Point(5,0,0).data)

def test_body_axis_rates_constant():
    ps = Quaternion.body_axis_rates(Q0(), Q0()) 
    assert not np.any(np.isnan(ps.data))

def test_body_diff_constant():
    ps = Euler(0,0,0).tile(20).body_diff(np.ones(20))
    assert not np.any(np.isnan(ps.data))



#@mark.skip("to be thought about later")        
def test_from_rotation_matrix():

    np.testing.assert_array_equal(Quaternion.zero().to_rotation_matrix()[0], np.identity(3))
    np.testing.assert_array_equal(
        Quaternion.from_rotation_matrix(np.identity(3)).data[0], 
        Quaternion.zero().data[0]
    )


def test_closest_principal():
    np.testing.assert_array_almost_equal(
        Euldeg(
           np.array( [
                [0, 95, 95],
                [20, 10, 30],
                [91, 1, 40],
            ])
        ).closest_principal().data,
        Euldeg(
            np.array([
                [0, 90, 90],
                [0, 0, 0],
                [90, 0, 0],
            ])
        ).data
    )


def test_squad():
    p = Q0()
    a = Euler(0,0,0)
    b = Euler(90, 0, 0)
    q = Euler(90, 0, 0)
    res = Quaternion.concatenate([Quaternion.squad(p, a, b, q)(t) for t in np.linspace(0,1,100)])   
    ps = res.transform_point(PY())
    fig = ps.plot(mode="lines")
    pis = Quaternion.concatenate([p, a,b,q]).transform_point(PY())
    fig.add_traces(pis.plot(index=[0, 33,66,100],mode="markers").data)
    fig.show()

def test_slerp():
    qs = Quaternion.concatenate([Euldeg(0,0,90*i) for i in range(5)])
    #qs.plot_3d(vis="plane").show()
    q_halfs = qs.slerp()(np.arange(9)/2)
    assert not np.any(np.isnan(q_halfs.data))
    #I think this should not fail:
    #np.testing.assert_array_almost_equal(q_halfs.body_diff().z[::2], qs.body_diff().z /2)
    
    pass



@mark.skip("to be thought about later")
def test_backward_diff_problem():
    data = pd.read_csv('tests/quat_body_diff_test.csv')
    ps = Quaternion(data.iloc[:,1:]).body_diff(data.iloc[:,0].to_numpy())
    assert np.mean(ps.y[100:200]) > 0
   # rmats = np.array([
   #     np.identity(3),
   #     Point(1, 1, 0).to_rotation_matrix()[0],
   #     Point(0.7, -1.2, 1).to_rotation_matrix()[0]
   # ])
#
   # quats = Quaternion.from_rotation_matrix(rmats)
#
   # rmat2 = quats.to_rotation_matrix()
#
   #     
   # np.testing.assert_array_equal(rmats, rmat2)



