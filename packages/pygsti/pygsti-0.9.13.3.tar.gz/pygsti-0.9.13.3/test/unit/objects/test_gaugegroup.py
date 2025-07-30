import numpy as np

from pygsti.modelmembers import operations as op
from pygsti.models import gaugegroup as ggrp
from pygsti.baseobjs.statespace import QubitSpace
from ..util import BaseCase


class GaugeGroupBase(object):

    def setUp(self):
        self.state_space = QubitSpace(1)
    
    def test_construction(self):
        params = self.gg.initial_params
        self.assertEqual(len(params), self.n_params)
        self.assertEqual(self.gg.num_params, self.n_params)
        element = self.gg.compute_element(params)
        # XXX is this necessary?  EGN: maybe not, but it asserts correctness and should be fast
        self.assertIsInstance(element, self.element_type)

    def test_element_construction(self):
        el = self.gg.compute_element(self.gg.initial_params)
        self.assertEqual(el.num_params, self.n_params)

    def test_element_get_transform_matrix(self):
        el = self.gg.compute_element(self.gg.initial_params)
        mx = el.transform_matrix
        # TODO assert correctness

    def test_element_get_transform_matrix_inverse(self):
        el = self.gg.compute_element(self.gg.initial_params)
        mx = el.transform_matrix
        inv = el.transform_matrix_inverse
        self.assertArraysAlmostEqual(np.linalg.inv(mx), inv)

    def test_element_deriv_wrt_params(self):
        el = self.gg.compute_element(self.gg.initial_params)
        deriv = el.deriv_wrt_params()
        # TODO assert correctness

    def test_element_to_vector(self):
        el = self.gg.compute_element(self.gg.initial_params)
        v = el.to_vector()
        # TODO assert correctness

    def test_element_from_vector(self):
        ip = self.gg.initial_params
        el = self.gg.compute_element(ip)
        el2 = self.gg.compute_element(ip)
        v = el.to_vector()
        el2.from_vector(v)
        self.assertArraysAlmostEqual(el.transform_matrix, el2.transform_matrix)
        # TODO does this actually assert correctness?


class GaugeGroupTester(GaugeGroupBase, BaseCase):
    # XXX do we need coverage of an abstract base class?
    # XXX should this class even be instantiatable?  EGN: no, it's just a base class.
    n_params = 0
    element_type = ggrp.GaugeGroupElement

    def setUp(self):
        self.gg = ggrp.GaugeGroup('myGaugeGroupName')

    def test_element_get_transform_matrix_inverse(self):
        el = self.gg.compute_element(self.gg.initial_params)
        inv = el.transform_matrix_inverse
        self.assertIsNone(inv)

    def test_element_from_vector(self):
        pass  # abstract


class OpGaugeGroupTester(GaugeGroupBase, BaseCase):
    n_params = 16
    element_type = ggrp.OpGaugeGroupElement

    def setUp(self):
        GaugeGroupBase.setUp(self)
        self.gg = ggrp.OpGaugeGroup(op.FullArbitraryOp(np.identity(4, 'd'), state_space=self.state_space),
                                    ggrp.OpGaugeGroupElement, 'myGateGaugeGroupName')


class FullGaugeGroupTester(GaugeGroupBase, BaseCase):
    n_params = 16
    element_type = ggrp.FullGaugeGroupElement

    def setUp(self):
        GaugeGroupBase.setUp(self)
        self.gg = ggrp.FullGaugeGroup(self.state_space)


class TPGaugeGroupTester(GaugeGroupBase, BaseCase):
    n_params = 12
    element_type = ggrp.TPGaugeGroupElement

    def setUp(self):
        GaugeGroupBase.setUp(self)
        self.gg = ggrp.TPGaugeGroup(self.state_space)


class DiagGaugeGroupTester(GaugeGroupBase, BaseCase):
    n_params = 4
    element_type = ggrp.DiagGaugeGroupElement

    def setUp(self):
        GaugeGroupBase.setUp(self)
        self.gg = ggrp.DiagGaugeGroup(self.state_space)


class TPDiagGaugeGroupTester(GaugeGroupBase, BaseCase):
    n_params = 3
    element_type = ggrp.TPDiagGaugeGroupElement

    def setUp(self):
        GaugeGroupBase.setUp(self)
        self.gg = ggrp.TPDiagGaugeGroup(self.state_space)


class SpamGaugeGroupTester(GaugeGroupBase, BaseCase):
    n_params = 2
    element_type = ggrp.SpamGaugeGroupElement

    def setUp(self):
        GaugeGroupBase.setUp(self)
        self.gg = ggrp.SpamGaugeGroup(self.state_space)


class TrivialGaugeGroupTester(GaugeGroupBase, BaseCase):
    n_params = 0
    element_type = ggrp.TrivialGaugeGroupElement

    def setUp(self):
        GaugeGroupBase.setUp(self)
        self.gg = ggrp.TrivialGaugeGroup(self.state_space)
