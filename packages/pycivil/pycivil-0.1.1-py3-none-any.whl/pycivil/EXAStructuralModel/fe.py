import json
import math
import os
from enum import Enum
from typing import List

import gmsh
import numpy as np
from gmsh import model as gmshModel
from jinja2 import Environment, FileSystemLoader
from pycivil import EXAExceptions as ex
from pycivil.EXAUtils import logging as log

thisPath = os.path.dirname(os.path.abspath(__file__))
sp = os.path.join(thisPath, "../../res/midas")

file_loader = FileSystemLoader(searchpath=sp)
env = Environment(loader=file_loader)
template = env.get_template("template-box.mgt")

# -----------------------------------------------------------------------------
#
#  Gmsh Python extended tutorial 1
#
#  Geometry and mesh data
#
# -----------------------------------------------------------------------------

# The Python API allows to do much more than what can be done in .geo files. These
# additional features are introduced gradually in the extended tutorials,
# starting with `x1.py'.

# In this first extended tutorial, we start by using the API to access basic
# geometrical and mesh data.


class Dim(Enum):
    DIM_0D = 0
    DIM_1D = 1
    DIM_2D = 2
    DIM_3D = 3


class Elem(Enum):
    ELEM_TRIA = 3
    ELEM_QUAD = 4


class FEModel:
    try:
        thisPath = os.path.dirname(os.path.abspath(__file__))
        f = open(os.path.join(thisPath, "../../res/EXAStructuralModel-config.json"))
        configData = json.load(f)
    except OSError as e:
        raise ex.EXAExceptions(
            "(EXAStructuralModel)-0001",
            "Cannont read config file",
            "../res/EXAStructuralModel-config.json",
        ) from e

    def __init__(self, descr="", modelName="default"):

        # GMSH init
        gmsh.initialize()

        # Using OCC as BREP for geometry
        self.__cad = gmshModel.occ

        # Adding model and make current
        gmshModel.add(modelName)
        gmshModel.setCurrent(modelName)

        self.__models = [modelName]

        print(gmshModel.list())

        self.__description = descr
        self.__loadCase = {}
        self.__loads = {}
        self.__nodeSupports = {}
        self.__nodeSprings = {}

        self.__sectionShapes = {
            1: {"type": "RECTANGULAR", "dimensions": [1.0, 0.3], "name": "default"}
        }
        self.__framesShapes = {}

        self.__logLevel = 3

    def __assignShapesToFrames(self):
        pass

    def __log(self, tp, msg):
        log.log(tp, msg, self.__logLevel)

    def show(self):
        gmsh.fltk.run()

    def addSectionShape(self, idShape, name, tp, dim=None):
        if dim is None:
            dim = []

        if idShape in self.__sectionShapes.keys():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0007", "idShape for shape must be unique", idShape
            )

        if not isinstance(idShape, int):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004", "idShape must be a int", type(idShape)
            )

        if not isinstance(tp, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004", "name must be a str", type(name)
            )

        if not isinstance(tp, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004", "tp must be a str", type(tp)
            )

        if not all(isinstance(n, float) for n in dim):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0009", "dim must be float list", type(dim)
            )
        else:
            np.array(dim, dtype=np.float32)

        tps = ["RECTANGULAR"]

        if tp not in tps:
            raise ex.EXAExceptions("(EXAStructuralModel)-0004", "tp unknown", type(tp))

        if tp == "RECTANGULAR":

            if len(dim) != 2:
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0004",
                    "For *RECTANGULAR* dim must have a two dim array",
                    len(dim),
                )

        self.__sectionShapes[idShape] = {
            type: "RECTANGULAR",
            "dimensions": dim,
            "name": name,
        }

    def sectionShapes(self):
        return self.__sectionShapes

    def assignFrameSectionShape(self, tagFrame, idShape):
        if not (isinstance(tagFrame, int) or isinstance(tagFrame, np.uint64)):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004", "tagFrame must be a int", type(tagFrame)
            )

        if not isinstance(idShape, int):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004", "idShape must be a int", type(idShape)
            )

        if idShape not in self.__sectionShapes.keys():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004",
                "idShape unknown in sectionShapes table",
                idShape,
            )

        self.__framesShapes[tagFrame] = idShape

    def frameSectionShape(self):
        return self.__framesShapes

    def assignMultiFrameSectionShape(self, idShape, tagsMacro=None, tagsFrames=None):
        if tagsMacro is None:
            tagsMacro = []
        if tagsFrames is None:
            tagsFrames = []

        if len(tagsMacro) == 0 and len(tagsFrames) == 0:
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004",
                "tagsMacro or tagsFrames must be null",
                len(tagsMacro),
            )

        if len(tagsMacro) != 0 and len(tagsFrames) != 0:
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004",
                "tagsMacro or tagsFrames must be not null",
                len(tagsMacro),
            )

        if len(tagsMacro) != 0:
            framesTags = self.framesModelTags()
            for tag in tagsMacro:
                for _i, t in enumerate(framesTags[tag]):
                    self.assignFrameSectionShape(t, idShape)
        else:
            for _i, t in enumerate(tagsFrames):
                self.assignFrameSectionShape(t, idShape)

    def clear(self):
        gmsh.clear()
        gmsh.finalize()

    def nodesTags(self):
        nt = []
        entities = gmshModel.getEntities()
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]
            # Get the mesh nodes for the entity (dim, tag):
            nodeTags, nodeCoords, nodeParams = gmsh.model.mesh.getNodes(dim, tag)
            nt += list(nodeTags)
        return nt

    def framesModelTags(self, filter=None):
        if filter is None:
            filter = []

        ft = {}
        entities = gmshModel.getEntities(1)
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]
            # Get the mesh nodes for the entity (dim, tag):
            elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(dim, tag)
            ft[tag] = list(elemTags[0])
        if len(filter) == 0:
            return ft
        else:
            tags = []
            for i in filter:
                tags += ft[i]
            return tags

    def framesTags(self):
        ft = []
        entities = gmshModel.getEntities(1)
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]
            # Get the mesh nodes for the entity (dim, tag):
            elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(dim, tag)
            ft += list(elemTags[0])
        return ft

    def framesModelNodeTags(self, filter=None):
        if filter is None:
            filter = []

        ft = {}
        entities = gmshModel.getEntities(1)
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]
            # Get the mesh nodes for the entity (dim, tag):
            elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(dim, tag)
            nt = []
            for a in elemNodeTags[0].reshape(round(len(elemNodeTags[0]) / 2), 2):
                nt += [list(a)]
            ft[tag] = nt

        if len(filter) == 0:
            return ft
        else:
            tags = []
            for i in filter:
                tags += ft[i]
            return tags

    def framesNodeTags(self):
        ft = []
        entities = gmshModel.getEntities(1)
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]
            # Get the mesh nodes for the entity (dim, tag):
            elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(dim, tag)
            nt = []
            for a in elemNodeTags[0].reshape(round(len(elemNodeTags[0]) / 2), 2):
                nt += [list(a)]
            ft += nt

        return ft

    def nodesCoords(self):
        nc = []
        entities = gmshModel.getEntities()
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]

            # Get the mesh nodes for the entity (dim, tag):
            nodeTags, nodeCoords, nodeParams = gmsh.model.mesh.getNodes(dim, tag)
            nc += nodeCoords.reshape(round(len(nodeCoords) / 3), 3).tolist()
        return nc

    def nodesGroups(self):
        ng = {}
        entities = gmshModel.getEntities(0)
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]
            ng[tag] = list(gmshModel.getPhysicalGroupsForEntity(dim, tag))
        return ng

    def framesGroups(self):
        fg = {}
        entities = gmshModel.getEntities(1)
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]
            fg[tag] = list(gmshModel.getPhysicalGroupsForEntity(dim, tag))
        return fg

    def printNodes(self):

        entities = gmshModel.getEntities()
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]

            # Get the mesh nodes for the entity (dim, tag):
            nodeTags, nodeCoords, nodeParams = gmsh.model.mesh.getNodes(dim, tag)
            print("nodeTags", nodeTags)
            print("nodeCoords", nodeCoords)
            print("phisicalGroup", gmshModel.getPhysicalGroupsForEntity(dim, tag))

    def printFrames(self):

        entities = gmshModel.getEntities(1)
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]

            # Get the mesh elements for the entity (dim, tag):
            elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(dim, tag)
            print("elemTypes", elemTypes)
            print("elemTags", elemTags)
            print("elemNodeTags", elemNodeTags)
            print("phisicalGroup", gmshModel.getPhysicalGroupsForEntity(dim, tag))

    def printElements(self):
        entities = gmshModel.getEntities()
        for e in entities:
            # Dimension and tag of the entity:
            dim = e[0]
            tag = e[1]

            # Get the mesh elements for the entity (dim, tag):
            elemTypes, elemTags, elemNodeTags = gmsh.model.mesh.getElements(dim, tag)
            print("elemTypes", elemTypes)
            print("elemTags", elemTags)
            print("elemNodeTags", elemNodeTags)
            print("phisicalGroup", gmshModel.getPhysicalGroupsForEntity(dim, tag))

    def addLoadCase(self, id, tp="U", descr=""):

        if not isinstance(id, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0002", "First arg must be a string", id
            )
        if not isinstance(tp, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0003", "Second arg must be a string", tp
            )
        else:
            find = False
            for v in self.configData["LoadCaseType"]:
                if v["id"] == tp:
                    find = True
                    print(
                        "Type *{}* of load case generic *{}*: {} ---> {}".format(
                            id, v["id"], v["description"], descr
                        )
                    )
                    break
            if not find:
                raise ex.EXAExceptions("(EXAStructuralModel)-0005", "Type unknown", tp)

        if not isinstance(tp, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0004", "Third arg must be a string", descr
            )

        if id in self.__loadCase.keys():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0006", "Load case must be unique", id
            )

        self.__loadCase[id] = [tp, descr]

    def getLoads(self):
        return self.__loads

    def addSelfWeight(self, loadCase, GCS):
        if not isinstance(loadCase, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0007", "First arg must be a string", loadCase
            )

        if loadCase not in self.__loadCase.keys():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0008", "Load case unknown", loadCase
            )

        if not all(isinstance(n, float) for n in GCS):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0009", "GCS must be float list", GCS
            )

        if len(GCS) != 3:
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0010", "GCS must have len 3", len(GCS)
            )

        if loadCase not in self.__loads:
            self.__loads[loadCase] = {}

        self.__loads[loadCase]["selfWeight"] = GCS

    def addMultiFrameWinklerSpring(self, tagsMacro, tp, dir, subgradeModulus, Bref):
        # subgradeModulus: modulo di sottofondo alla Winkler
        # Bref: largezza di riferimento per il calcolo della pressione

        if not isinstance(tagsMacro, list):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0011", "tagsMacro must be a list", type(tagsMacro)
            )

        nodesTags = self.nodesTags()
        nodesCoords = self.nodesCoords()
        framesTags = self.framesModelTags()
        frameNodes = self.framesModelNodeTags()

        for tag in tagsMacro:
            # TODO: move this in separate function for subFrames (meshed frames) and add tagsFrames
            #       in function args with two cases
            for i, _t in enumerate(framesTags[tag]):
                n1 = frameNodes[tag][i][0]
                n2 = frameNodes[tag][i][1]
                n1_coords = nodesCoords[nodesTags.index(n1)]
                n2_coords = nodesCoords[nodesTags.index(n2)]

                if "DX" in dir:
                    idxDir1 = 1
                    idxDir2 = 2
                elif "DY" in dir:
                    idxDir1 = 0
                    idxDir2 = 2
                elif "DZ" in dir:
                    idxDir1 = 0
                    idxDir2 = 0

                tributaryLength = math.sqrt(
                    pow(n2_coords[idxDir1] - n1_coords[idxDir1], 2)
                    + pow(n2_coords[idxDir2] - n1_coords[idxDir2], 2)
                )

                stiffness = tributaryLength * subgradeModulus * Bref

                self.addNodeSpring(n1, tp, dir, stiffness, add=True)
                self.addNodeSpring(n2, tp, dir, stiffness, add=True)

    def addMultiFrameLoadHydro(self, loadCase, tagsMacro, dir, gamma, K, H0, p0, Bref):
        # gamma: peso del terreno specifico
        # K: coefficiente di spinta del terreno
        # H0: distanza dallo zero della copertura del terreno
        # p0: pressione di partenza ovvero il sovraccarico
        # Bref: largezza di riferimento per il calcolo della pressione

        if not isinstance(loadCase, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0011",
                "First arg must be a string",
                type(loadCase),
            )

        if not isinstance(tagsMacro, list):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0011", "tagsMacro must be a list", type(tagsMacro)
            )

        if dir not in ("GCX", "GCY", "GCZ"):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022",
                "Third arg *dir* must be GCX, GCY, GCZ",
                dir,
            )

        nodesTags = self.nodesTags()
        nodesCoords = self.nodesCoords()
        framesTags = self.framesModelTags()
        frameNodes = self.framesModelNodeTags()

        for tag in tagsMacro:
            # TODO: move this in separate function for subFrames (meshed frames) and add tagsFrames
            #       in function args with two cases
            for i, t in enumerate(framesTags[tag]):
                n1 = frameNodes[tag][i][0]
                n2 = frameNodes[tag][i][1]
                n1_coords = nodesCoords[nodesTags.index(n1)]
                n2_coords = nodesCoords[nodesTags.index(n2)]
                press_1 = ((H0 - n1_coords[2]) * gamma * K + p0) * Bref
                press_2 = ((H0 - n2_coords[2]) * gamma * K + p0) * Bref
                if dir == "GCX":
                    self.addFrameLoad(
                        loadCase,
                        t,
                        tp="force",
                        GCX1=[0.0, press_1],
                        GCX2=[1.0, press_2],
                    )
                elif dir == "GCY":
                    self.addFrameLoad(
                        loadCase,
                        t,
                        tp="force",
                        GCY1=[0.0, press_1],
                        GCY2=[1.0, press_2],
                    )
                elif dir == "GCZ":
                    self.addFrameLoad(
                        loadCase,
                        t,
                        tp="force",
                        GCZ1=[0.0, press_1],
                        GCZ2=[1.0, press_2],
                    )
                else:
                    raise ex.EXAExceptions(
                        "(EXAStructuralModel)-0011", "unknown error in dir", type(dir)
                    )

    def addMultiFrameLoad(
        self,
        loadCase,
        tagsFrames,
        tp="force",
        GCX1=None,
        GCX2=None,
        GCY1=None,
        GCY2=None,
        GCZ1=None,
        GCZ2=None,
    ):
        if GCX1 is None:
            GCX1 = []
        if GCX2 is None:
            GCX2 = []
        if GCY1 is None:
            GCY1 = []
        if GCY2 is None:
            GCY2 = []
        if GCZ1 is None:
            GCZ1 = []
        if GCZ2 is None:
            GCZ2 = []

        if not isinstance(tagsFrames, list):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0011",
                "tagsFrames must be a list",
                type(tagsFrames),
            )

        for tag in tagsFrames:
            self.addFrameLoad(loadCase, tag, tp, GCX1, GCX2, GCY1, GCY2, GCZ1, GCZ2)

    def addFrameLoad(
        self,
        loadCase,
        tagFrame,
        tp="force",
        GCX1=None,
        GCX2=None,
        GCY1=None,
        GCY2=None,
        GCZ1=None,
        GCZ2=None,
    ):
        if GCX1 is None:
            GCX1 = []
        if GCX2 is None:
            GCX2 = []
        if GCY1 is None:
            GCY1 = []
        if GCY2 is None:
            GCY2 = []
        if GCZ1 is None:
            GCZ1 = []
        if GCZ2 is None:
            GCZ2 = []

        if not isinstance(loadCase, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0011",
                "First arg must be a string",
                type(loadCase),
            )

        if loadCase not in self.__loadCase.keys():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0012", "Load case unknown", loadCase
            )

        if tagFrame not in self.framesTags():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0013", "Frames tag unknown", tagFrame
            )

        if not isinstance(tp, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0014", "Third arg must be a string", type(tp)
            )

        if all(["force" != tp, "moment" != tp]):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0015", "tp option *force* or *moment*", tp
            )

        cond_null_X = all([len(GCX1) == 0, len(GCX2) == 0])
        cond_null_Y = all([len(GCY1) == 0, len(GCY2) == 0])
        cond_null_Z = all([len(GCZ1) == 0, len(GCZ2) == 0])

        if not cond_null_X:
            if len(GCX1) != 2:
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0016", "GCX1 must have len 2", len(GCX1)
                )

            if not all(isinstance(n, float) for n in GCX1):
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0017", "GCX1 must be float list", GCX1
                )

            if len(GCX2) != 2 and len(GCX2) != 0:
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0018", "GCX2 must have len 2 or 0", GCX2
                )

            if len(GCX2) == 0:
                GCX2 = GCX1[:]
                GCX2[0] = 1.0

        if not cond_null_Y:
            if len(GCY1) != 2:
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0019", "GCY1 must have len 2", len(GCY1)
                )

            if not all(isinstance(n, float) for n in GCY1):
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0017", "GCY1 must be float list", GCY1
                )

            if len(GCY2) != 2 and len(GCY2) != 0:
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0021", "GCX2 must have len 2 or 0", GCY2
                )

            if len(GCY2) == 0:
                GCY2 = GCY1[:]
                GCY2[0] = 1.0

        if not cond_null_Z:
            if len(GCZ1) != 2:
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0022", "GCZ1 must have len 2", len(GCZ1)
                )

            if not all(isinstance(n, float) for n in GCZ1):
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0017", "GCZ1 must be float list", GCZ1
                )

            if len(GCZ1) != 2 and len(GCZ1) != 0:
                raise ex.EXAExceptions(
                    "(EXAStructuralModel)-0024", "GCX2 must have len 2 or 0", GCZ1
                )

            if len(GCZ2) == 0:
                GCZ2 = GCZ1[:]
                GCZ2[0] = 1.0

        if loadCase not in self.__loads:
            self.__loads[loadCase] = {}

        if "frameLoad" not in self.__loads[loadCase]:
            self.__loads[loadCase]["frameLoad"] = {}

        if tagFrame not in self.__loads[loadCase]["frameLoad"].keys():
            self.__loads[loadCase]["frameLoad"][tagFrame] = {}

        if tp not in self.__loads[loadCase]["frameLoad"][tagFrame].keys():
            self.__loads[loadCase]["frameLoad"][tagFrame][tp] = {}

        if not cond_null_X:
            self.__loads[loadCase]["frameLoad"][tagFrame][tp]["GCX1"] = GCX1
            self.__loads[loadCase]["frameLoad"][tagFrame][tp]["GCX2"] = GCX2

        if not cond_null_Y:
            self.__loads[loadCase]["frameLoad"][tagFrame][tp]["GCY1"] = GCY1
            self.__loads[loadCase]["frameLoad"][tagFrame][tp]["GCY2"] = GCY2

        if not cond_null_Z:
            self.__loads[loadCase]["frameLoad"][tagFrame][tp]["GCZ1"] = GCZ1
            self.__loads[loadCase]["frameLoad"][tagFrame][tp]["GCZ2"] = GCZ2

    def addMultiNodeLoad(self, loadCase, tagsNodes, NCS):
        if not isinstance(tagsNodes, list):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0018", "tagsNodes arg must be a list", tagsNodes
            )

        for tag in tagsNodes:
            self.addNodeLoad(loadCase, tag, NCS)

    def addNodeLoad(self, loadCase, tagNode, NCS):
        if not isinstance(loadCase, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0018", "First arg must be a string", loadCase
            )

        if loadCase not in self.__loadCase.keys():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0019", "Load case unknown", loadCase
            )

        if tagNode not in self.nodesTags():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0020", "Nodes tag unknown", tagNode
            )

        if not all(isinstance(n, float) for n in NCS):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0021", "NCS must be float list", NCS
            )

        if len(NCS) != 6:
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022", "NCS must have len 6", len(NCS)
            )

        if loadCase not in self.__loads:
            self.__loads[loadCase] = {}

        if "nodeLoad" not in self.__loads[loadCase]:
            self.__loads[loadCase]["nodeLoad"] = {}

        self.__loads[loadCase]["nodeLoad"][tagNode] = {"NCS": NCS}

    def addMultiNodeContraints(self, tagsNodes, dof):
        if not isinstance(tagsNodes, list):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0018", "tagsNodes arg must be a list", tagsNodes
            )

        for tag in tagsNodes:
            self.addNodeContraints(tag, dof)

    def addNodeContraints(self, tagNode, dof):
        if tagNode not in self.nodesTags():
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0034", "Nodes tag unknown", tagNode
            )

        if not all(isinstance(n, int) for n in dof):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0021", "dof must be int list", dof
            )

        if len(dof) != 6:
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022", "dof must have len 6", len(dof)
            )

        self.__nodeSupports[tagNode] = dof

    def getNodeContraints(self):
        return self.__nodeSupports

    def addMultiNodeSpring(self, tagsNodes, tp, dir, stiffness):
        if not isinstance(tagsNodes, list):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0018", "tagsNodes arg must be a list", tagsNodes
            )

        for tag in tagsNodes:
            self.addNodeSpring(tag, tp, dir, stiffness)

    def addNodeSpring(self, tagNode, tp, dir, stiffness, add=False):
        if not (isinstance(tagNode, int) or isinstance(tagNode, np.uint64)):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022",
                "First arg *tagNode* must be int or numpy.uint64",
                tagNode,
            )

        if not isinstance(tp, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022", "Second arg *tp* must be str", tp
            )

        if tp not in ("LINEAR", "COMP", "TENS"):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022",
                "Second arg *tp* must be LINEAR, COMP or TENS",
                tp,
            )

        if not isinstance(dir, str):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022", "Third arg *dir* must be str", dir
            )

        if dir not in ("DX+", "DX-", "DY+", "DY-", "DZ+", "DZ-"):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022", "Third arg *dir* must be DX+ ... DZ-", dir
            )

        if not isinstance(stiffness, float):
            raise ex.EXAExceptions(
                "(EXAStructuralModel)-0022",
                "Fourth arg *stiffness* must be float",
                stiffness,
            )

        if tagNode not in self.__nodeSprings.keys():
            self.__nodeSprings[tagNode] = {}

        if tp not in self.__nodeSprings[tagNode].keys():
            self.__nodeSprings[tagNode][tp] = {}

        if dir in self.__nodeSprings[tagNode][tp] and add:
            self.__nodeSprings[tagNode][tp][dir] += stiffness
        else:
            self.__nodeSprings[tagNode][tp][dir] = stiffness

    def getNodeStrings(self):
        return self.__nodeSprings

    def getNodesPhysicalName(self):
        groups = gmshModel.getPhysicalGroups(0)
        names = []
        for g in groups:
            names.append(gmshModel.getPhysicalName(g[0], g[1]))
        return names

    def getFramesPhysicalName(self):
        groups = gmshModel.getPhysicalGroups(1)
        names = []
        for g in groups:
            names.append(gmshModel.getPhysicalName(g[0], g[1]))
        return names

    def getNodesByPhysicalName(self, name):
        groups = gmshModel.getPhysicalGroups(0)
        for g in groups:
            if name == gmshModel.getPhysicalName(g[0], g[1]):
                return list(gmshModel.getEntitiesForPhysicalGroup(g[0], g[1]))
        return []

    def getNodesByPhysicalGroup(self, tagGroup):
        groups = gmshModel.getPhysicalGroups(0)
        for g in groups:
            if g[1] == tagGroup:
                return list(gmshModel.getEntitiesForPhysicalGroup(g[0], g[1]))
        return []

    def getFramesByPhysicalName(self, name):
        groups = gmshModel.getPhysicalGroups(1)
        for g in groups:
            if name == gmshModel.getPhysicalName(g[0], g[1]):
                return list(gmshModel.getEntitiesForPhysicalGroup(g[0], g[1]))
        return []

    def getFramesByPhysicalGroup(self, tagGroup):
        groups = gmshModel.getPhysicalGroups(1)
        for g in groups:
            if g[1] == tagGroup:
                return list(gmshModel.getEntitiesForPhysicalGroup(g[0], g[1]))
        return []

    def __save_mgt(self, fileName):
        # ----------------
        # *NODE    ; Nodes
        # ; iNO, X, Y, Z
        # ----------------
        nodes = []
        nodesTags = self.nodesTags()
        nodesCoords = self.nodesCoords()
        for i, n in enumerate(nodesTags):
            strFormat = "{id:d},{x:.6f},{y:.6f},{z:.6f}"
            formatted = strFormat.format(
                id=n, x=nodesCoords[i][0], y=nodesCoords[i][1], z=nodesCoords[i][2]
            )
            nodes.append(formatted)

        # ------------------------------------------------------------------------------------
        # *ELEMENT    ; Elements
        # ; iEL, TYPE, iMAT, iPRO, iN1, iN2, ANGLE, iSUB,                     ; Frame  Element
        # ; iEL, TYPE, iMAT, iPRO, iN1, iN2, ANGLE, iSUB, EXVAL, EXVAL2, bLMT ; Comp/Tens Truss
        # ; iEL, TYPE, iMAT, iPRO, iN1, iN2, iN3, iN4, iSUB, iWID , LCAXIS    ; Planar Element
        # ; iEL, TYPE, iMAT, iPRO, iN1, iN2, iN3, iN4, iN5, iN6, iN7, iN8     ; Solid  Element
        # ------------------------------------------------------------------------------------
        frames = []
        framesTags = self.framesTags()
        framesNodeTags = self.framesNodeTags()

        for i, f in enumerate(framesTags):
            if f in self.__framesShapes.keys():
                idShape = self.__framesShapes[f]
            else:
                idShape = 1
            strFormat = "{id:d},BEAM,1,{iPRO:d},{idStart:d},{idEnd:d},0,0"
            formatted = strFormat.format(
                id=f,
                iPRO=idShape,
                idStart=framesNodeTags[i][0],
                idEnd=framesNodeTags[i][1],
            )
            frames.append(formatted)

        # -----------------------------------------------------------------------------------------------------------
        # *SECTION    ; Section
        # ; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE, [DATA1], [DATA2]                    ; 1st line - DB/USER
        # ; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE, BLT, D1, ..., D8, iCEL              ; 1st line - VALUE
        # ;       AREA, ASy, ASz, Ixx, Iyy, Izz                                               ; 2nd line
        # ;       CyP, CyM, CzP, CzM, QyB, QzB, PERI_OUT, PERI_IN, Cy, Cz                     ; 3rd line
        # ;       Y1, Y2, Y3, Y4, Z1, Z2, Z3, Z4, Zyy, Zzz                                    ; 4th line
        # ; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE, ELAST, DEN, POIS, POIC, SF, THERMAL ; 1st line - SRC
        # ;       D1, D2, [SRC]                                                               ; 2nd line
        # ; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE, 1, DB, NAME1, NAME2, D1, D2         ; 1st line - COMBINED
        # ; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE, 2, D11, D12, D13, D14, D15, D21, D22, D23, D24
        # ; iSEC, TYPE, SNAME, [OFFSET2], bSD, bWE, SHAPE, iyVAR, izVAR, STYPE                ; 1st line - TAPERED
        # ;       DB, NAME1, NAME2                                                            ; 2nd line(STYPE=DB)
        # ;       [DIM1], [DIM2]                                                              ; 2nd line(STYPE=USER)
        # ;       D11, D12, D13, D14, D15, D16, D17, D18                                      ; 2nd line(STYPE=VALUE)
        # ;       AREA1, ASy1, ASz1, Ixx1, Iyy1, Izz1                                         ; 3rd line(STYPE=VALUE)
        # ;       CyP1, CyM1, CzP1, CzM1, QyB1, QzB1, PERI_OUT1, PERI_IN1, Cy1, Cz1           ; 4th line(STYPE=VALUE)
        # ;       Y11, Y12, Y13, Y14, Z11, Z12, Z13, Z14, Zyy1, Zyy2                          ; 5th line(STYPE=VALUE)
        # ;       D21, D22, D23, D24, D25, D26, D27, D28                                      ; 6th line(STYPE=VALUE)
        # ;       AREA2, ASy2, ASz2, Ixx2, Iyy2, Izz2                                         ; 7th line(STYPE=VALUE)
        # ;       CyP2, CyM2, CzP2, CzM2, QyB2, QzB2, PERI_OUT2, PERI_IN2, Cy2, Cz2           ; 8th line(STYPE=VALUE)
        # ;       Y21, Y22, Y23, Y24, Z21, Z22, Z23, Z24, Zyy2, Zzz2                          ; 9th line(STYPE=VALUE)
        # ; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE                                      ; 1st line - COMPOSITE-B
        # ;       Hw, tw, B1, Bf1, tf1, B2, Bf2, tf2                                          ; 2nd line
        # ;       [SHAPE-NUM], [STIFF-SHAPE], [STIFF-POS] (1~4)                               ; 3rd line
        # ;       SW, GN, CTC, Bc, Tc, Hh, EsEc, DsDc, Ps, Pc, TsTc, bMulti, Elong, Esh       ; 4th line
        # ; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE                                      ; 1st line - COMPOSITE-I
        # ;       Hw, tw, B1, tf1, B2, tf2                                                    ; 2nd line
        # ;       [SHAPE-NUM], [STIFF-SHAPE], [STIFF-POS] (1~2)                               ; 3rd line
        # ;       SW, GN, CTC, Bc, Tc, Hh, EsEc, DsDc, Ps, Pc, TsTc, bMulti, Elong, Esh       ; 4th line
        # ; iSEC, TYPE, SNAME, [OFFSET], bSD, bWE, SHAPE                                      ; 1st line - COMPOSITE-TUB
        # ;       Hw, tw, B1, Bf1, tf1, B2, Bf2, tf2, Bf3, tfp                                ; 2nd line
        # ;       [SHAPE-NUM], [STIFF-SHAPE], [STIFF-POS] (1~3)                               ; 3rd line
        # ;       SW, GN, CTC, Bc, Tc, Hh, EsEc, DsDc, Ps, Pc, TsTc, bMulti, Elong, Esh       ; 4th line
        # ; [DATA1] : 1, DB, NAME or 2, D1, D2, D3, D4, D5, D6, D7, D8, D9, D10
        # ; [DATA2] : CCSHAPE or iCEL or iN1, iN2
        # ; [SRC]  : 1, DB, NAME1, NAME2 or 2, D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, iN1, iN2
        # ; [DIM1], [DIM2] : D1, D2, D3, D4, D5, D6, D7, D8
        # ; [OFFSET] : OFFSET, iCENT, iREF, iHORZ, HUSER, iVERT, VUSER
        # ; [OFFSET2]: OFFSET, iCENT, iREF, iHORZ, HUSERI, HUSERJ, iVERT, VUSERI, VUSERJ
        # ; [SHAPE-NUM]: SHAPE-NUM, POS, STIFF-NUM1, STIFF-NUM2, STIFF-NUM3, STIFF-NUM4
        # ; [STIFF-SHAPE]: SHAPE-NUM, for(SHAPE-NUM) { NAME, SIZE1~8 }
        # ; [STIFF-POS]: STIFF-NUM, for(STIFF-NUM) { SPACING, iSHAPE, bCALC }
        # -----------------------------------------------------------------------------------------------------------

        sections = []
        for k, v in self.__sectionShapes.items():
            strFormat = "{idShape:>8d},DBUSER,{name:>16s}, CC, 0, 0, 0, 0, 0, 0, YES, NO, SB, 2,{width:>8.3f},{height:>8.3f},0,0,0,0,0,0,0,0"
            formatted = strFormat.format(
                idShape=k,
                name=v["name"],
                width=v["dimensions"][0],
                height=v["dimensions"][1],
            )
            sections.append(formatted)

            # --------------------------------
        # *STLDCASE    ; Static Load Cases
        # ; LCNAME, LCTYPE, DESC
        # --------------------------------
        loadCases = []
        for k in self.__loadCase.keys():
            v = self.__loadCase[k]
            strFormat = "{LCNAME:>8s},{LCTYPE:>3s},{DESC:>40s}"
            formatted = strFormat.format(LCNAME=k, LCTYPE=v[0], DESC=v[1])
            loadCases.append(formatted)

        # --------------------------------------------
        # *CONSTRAINT    ; Supports
        # ; NODE_LIST, CONST(Dx,Dy,Dz,Rx,Ry,Rz), GROUP
        # --------------------------------------------
        nodeContraints = []
        if len(self.__nodeSupports) > 0:
            nodeContraints.append("*CONSTRAINT")
            for k, v in self.__nodeSupports.items():
                strFormat = "{tag:d},{TX:d}{TY:d}{TZ:d}{RX:d}{RY:d}{RZ:d}"
                formatted = strFormat.format(
                    tag=k, TX=v[0], TY=v[1], TZ=v[2], RX=v[3], RY=v[4], RZ=v[5]
                )
                nodeContraints.append(formatted)

        # -----------------------------------------------------------------------------------------------------------------
        # *SPRING    ; Point Spring Supports
        # ; NODE_LIST, Type, F_SDx, F_SDy, F_SDz, F_SRx, F_SRy, F_SRz, SDx, SDy, SDz, SRx, SRy, SRz ...
        # ;                  DAMPING, Cx, Cy, Cz, CRx, CRy, CRz, GROUP, [DATA1]                                ; LINEAR
        # ; NODE_LIST, Type, Direction, Vx, Vy, Vz, Stiffness, GROUP, [DATA1]                                  ; COMP, TENS
        # ; NODE_LIST, Type, Direction, Vx, Vy, Vz, FUNCTION, GROUP, [DATA1]                                   ; MULTI
        # ; [DATA1] EFFAREA, Kx, Ky, Kz
        # -----------------------------------------------------------------------------------------------------------------
        springs = []
        if len(self.__nodeSprings) > 0:
            springs.append("*SPRING")
            for k, v in self.__nodeSprings.items():
                for kk, vv in v.items():
                    if kk == "COMP":
                        Type = "COMP"
                    elif kk == "TENS":
                        Type = "TENS"
                    elif kk == "LINEAR":
                        Type = "LINEAR"
                    else:
                        raise ex.EXAExceptions(
                            "(EXAStructuralModel)-0026", "key error in Type", Type
                        )
                    for kkk, vvv in vv.items():
                        if kkk == "DX+":
                            Direction = 0
                        elif kkk == "DX-":
                            Direction = 1
                        elif kkk == "DY+":
                            Direction = 2
                        elif kkk == "DY-":
                            Direction = 3
                        elif kkk == "DZ+":
                            Direction = 4
                        elif kkk == "DZ-":
                            Direction = 5
                        else:
                            raise ex.EXAExceptions(
                                "(EXAStructuralModel)-0026",
                                "key error in Direction",
                                Direction,
                            )
                        strFormat = "{tag:d},{Type:s},{Direction:d},0,0,0,{Stiffness:.6f}, , 0, 0, 0, 0, 0"
                        formatted = strFormat.format(
                            tag=k, Type=Type, Direction=Direction, Stiffness=vvv
                        )
                        springs.append(formatted)
            springs.append("")

        # -----------------
        # *USE-STLD, <name>
        # -----------------
        loadCasesUsed = []
        for k, v in self.__loads.items():
            strFormat = "*USE-STLD, {key:s}"
            formatted = strFormat.format(key=k)
            loadCasesUsed.append(formatted)
            loadCasesUsed.append("")
            for kk, vv in v.items():
                if kk == "frameLoad":
                    loadCasesUsed.append("*BEAMLOAD")
                    # *BEAMLOAD    ; Element Beam Loads
                    # ; ELEM_LIST, CMD, TYPE, DIR, bPROJ, [ECCEN], [VALUE], GROUP
                    # ; ELEM_LIST, CMD, TYPE, TYPE, DIR, VX, VY, VZ, bPROJ, [ECCEN], [VALUE], GROUP
                    # ; [VALUE]       : D1, P1, D2, P2, D3, P3, D4, P4
                    # ; [ECCEN]       : bECCEN, ECCDIR, I-END, J-END, bJ-END
                    # ; [ADDITIONAL]  : bADDITIONAL, ADDITIONAL_I-END, ADDITIONAL_J-END, bADDITIONAL_J-END
                    for kkk, vvv in vv.items():

                        for kkkk, vvvv in vvv.items():
                            if kkkk == "force":
                                tp = "UNILOAD"
                            elif kkkk == "moment":
                                tp = "UNIMOMENT"
                            else:
                                raise ex.EXAExceptions(
                                    "(EXAStructuralModel)-0026", "key error in tp", tp
                                )

                            if "GCX1" in vvvv.keys() and "GCX2" in vvvv.keys():
                                strFormat = "{tag: d}, BEAM   , {tp}, GX, NO , NO, aDir[1], , , , {GCX1D:.6f}, {GCX1P:.6f}, {GCX2D:.6f}, {GCX2P:.6f}, 0, 0, 0, 0, , NO, 0, 0, NO,"
                                formatted = strFormat.format(
                                    tag=kkk,
                                    tp=tp,
                                    GCX1D=vvvv["GCX1"][0],
                                    GCX1P=vvvv["GCX1"][1],
                                    GCX2D=vvvv["GCX2"][0],
                                    GCX2P=vvvv["GCX2"][1],
                                )
                                loadCasesUsed.append(formatted)
                            if "GCY1" in vvvv.keys() and "GCY2" in vvvv.keys():
                                strFormat = "{tag: d}, BEAM   , {tp}, GY, NO , NO, aDir[1], , , , {GCY1D:.6f}, {GCY1P:.6f}, {GCY2D:.6f}, {GCY2P:.6f}, 0, 0, 0, 0, , NO, 0, 0, NO,"
                                formatted = strFormat.format(
                                    tag=kkk,
                                    tp=tp,
                                    GCY1D=vvvv["GCY1"][0],
                                    GCY1P=vvvv["GCY1"][1],
                                    GCY2D=vvvv["GCY2"][0],
                                    GCY2P=vvvv["GCY2"][1],
                                )
                                loadCasesUsed.append(formatted)
                            if "GCZ1" in vvvv.keys() and "GCZ2" in vvvv.keys():
                                strFormat = "{tag: d}, BEAM   , {tp}, GZ, NO , NO, aDir[1], , , , {GCZ1D:.6f}, {GCZ1P:.6f}, {GCZ2D:.6f}, {GCZ2P:.6f}, 0, 0, 0, 0, , NO, 0, 0, NO,"
                                formatted = strFormat.format(
                                    tag=kkk,
                                    tp=tp,
                                    GCZ1D=vvvv["GCZ1"][0],
                                    GCZ1P=vvvv["GCZ1"][1],
                                    GCZ2D=vvvv["GCZ2"][0],
                                    GCZ2P=vvvv["GCZ2"][1],
                                )
                                loadCasesUsed.append(formatted)

                    loadCasesUsed.append("")

                elif kk == "nodeLoad":
                    loadCasesUsed.append("*CONLOAD")
                    # *CONLOAD    ; Nodal Loads
                    # ; NODE_LIST, FX, FY, FZ, MX, MY, MZ, GROUP
                    for kkk, vvv in vv.items():
                        strFormat = "{tag: d}, {FX:.6f}, {FY:.6f}, {FZ:.6f}, {MX:.6f}, {MY:.6f}, {MZ:.6f},"
                        formatted = strFormat.format(
                            tag=kkk,
                            FX=vvv["NCS"][0],
                            FY=vvv["NCS"][1],
                            FZ=vvv["NCS"][2],
                            MX=vvv["NCS"][3],
                            MY=vvv["NCS"][4],
                            MZ=vvv["NCS"][5],
                        )
                        loadCasesUsed.append(formatted)

                    loadCasesUsed.append("")

                elif kk == "selfWeight":
                    loadCasesUsed.append("*SELFWEIGHT")
                    strFormat = "{DIRX: .6f}, {DIRY: .6f}, {DIRZ: .6f},"
                    formatted = strFormat.format(DIRX=vv[0], DIRY=vv[1], DIRZ=vv[2])
                    loadCasesUsed.append(formatted)
                    loadCasesUsed.append("")
                else:
                    raise ex.EXAExceptions(
                        "(EXAStructuralModel)-0025", "key error in loadCasesUsed", kk
                    )

            loadCasesUsed.append(
                f"; End of data for load case {k} -------------------------"
            )

        output = template.render(
            udm="KN,M, BTU, C",
            nodes=nodes,
            elements=frames,
            loadCases=loadCases,
            loadCasesUsed=loadCasesUsed,
            contraints=nodeContraints,
            springs=springs,
            sections=sections,
        )

        # print(output)

        with open(fileName + ".mgt", "w") as f:
            f.write(output)

    def save(self, fileName, fileType=".msh"):
        print("Write ", fileName + fileType)
        gmsh.option.setNumber("Mesh.SaveAll", 1)
        if fileType == ".msh":
            gmsh.write(fileName + fileType)
            # logGmshFile(fileName + fileType)
        elif fileType == ".med":
            gmsh.write(fileName + fileType)
        elif fileType == ".mgt":
            self.__save_mgt(fileName)
        else:
            self.__log("ERR", f"File type unknoun *{fileType}*. None file saved !!!")

    def getCad(self):
        return self.__cad

    def getModeler(self):
        return gmshModel

    def addModel(self, name: str) -> bool:
        if len(name) == 0:
            self.__log("ERR", "Arg must be a str not null !!!")
            return False
        else:
            if name in self.__models:
                self.__log("ERR", f"Model *{name}* is present !!!")
                return False
            else:
                gmshModel.add(name)
                self.__models.append(name)
                self.__log("INF", f"Model *{name}* added !!!")
                return True

    def getModels(self) -> List[str]:
        return self.__models

    def setCurrentModel(self, name: str) -> bool:
        if name not in self.__models:
            self.__log("ERR", f"Model *{name}* not present !!!")
            return False
        else:
            gmshModel.setCurrent(name)
            return True

    def addNodesToGroup(self, tags, tagGroup, physicalName=""):
        self.__addElementToGroup(tags, tagGroup, Dim.DIM_0D, physicalName)

    def __addElementToGroup(
        self, tags: List[int], tagGroup: int, dim: Dim, physicalName: str = ""
    ):
        gmshModel.addPhysicalGroup(dim.value, tags, tagGroup)
        if len(physicalName) > 0:
            gmshModel.setPhysicalName(dim.value, tagGroup, physicalName)

    def addFramesToGroup(self, tags, tagGroup, physicalName=""):
        self.__addElementToGroup(tags, tagGroup, Dim.DIM_1D, physicalName)

    def addNode(self, x, y, z, tag=-1, group=False, tagGroup=-1):
        tag = self.__cad.addPoint(x, y, z, meshSize=0.0, tag=tag)
        self.__cad.synchronize()
        if group:
            gmshModel.addPhysicalGroup(0, [tag], tag=tagGroup)
            # self.__cad.synchronize()
        return tag

    def addFrame(self, tagStart, tagEnd, tag=-1, group=False, tagGroup=-1, nb=1):
        tag = self.__cad.addLine(tagStart, tagEnd, tag=tag)
        self.__cad.synchronize()

        # mesh frame to have underlying mesh
        mesh = gmshModel.mesh
        mesh.setTransfiniteCurve(tag, nb + 1)
        mesh.generate(1)

        if group:
            gmshModel.addPhysicalGroup(1, [tag], tag=tagGroup)
            # self.__cad.synchronize()
        return tag

    def addPlateQuad(
        self,
        tagLine_1: int,
        tagLine_2: int,
        tagLine_3: int,
        tagLine_4: int,
        tag: int = -1,
        group: bool = False,
        tagGroup: int = -1,
        elType: Elem = Elem.ELEM_QUAD,
    ):
        wireId = self.__cad.addCurveLoop([tagLine_1, tagLine_2, tagLine_3, tagLine_4])
        plateId = self.__cad.addPlaneSurface(wireTags=[wireId], tag=tag)
        self.__cad.synchronize()
        mesh = gmshModel.mesh
        mesh.setTransfiniteSurface(tag=plateId, arrangement="left")
        if elType == Elem.ELEM_QUAD:
            mesh.setRecombine(dim=2, tag=plateId)

        mesh.generate(2)

        if group:
            gmshModel.addPhysicalGroup(2, [plateId], tag=tagGroup)
        return tag

    def addPlateQuadsToGroup(self, tags, tagGroup, physicalName=""):
        self.__addElementToGroup(tags, tagGroup, Dim.DIM_2D, physicalName)

    def addArc(self, tagStart, tagMid, tagEnd, tag=-1, group=False, tagGroup=-1, nb=10):
        tag = self.__cad.addCircleArc(tagStart, tagMid, tagEnd, tag=tag)
        self.__cad.synchronize()

        # mesh frame to have underlying mesh
        mesh = gmshModel.mesh
        mesh.setTransfiniteCurve(tag, nb + 1)
        mesh.generate(1)

        if group:
            gmshModel.addPhysicalGroup(1, [tag], tag=tagGroup)
            # self.__cad.synchronize()
        return tag

    def meshFrame(self, tag, nb):
        self.__cad.synchronize()
        mesh = gmshModel.mesh
        mesh.setTransfiniteCurve(tag, nb + 1)
        mesh.generate(1)
        elements = mesh.getElements()
        print(elements)

    def __str__(self):
        s = f"Model Description: {self.__description:s}"
        return s
