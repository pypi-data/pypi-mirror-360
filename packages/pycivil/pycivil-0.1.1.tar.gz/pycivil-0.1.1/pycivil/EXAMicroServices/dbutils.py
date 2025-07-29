import pprint
from typing import List
from uuid import UUID, uuid4

from pycivil.EXAMicroServices.models import User, UserRole
from pycivil.EXAUtils import dbtools


def buildDb():
    db = dbtools.DbManager()
    db.connect()
    if db.existsDb("swsmind"):
        return
    if (
        not db.newDb("swsmind")
        or not db.newCollection("users")
        or not db.newCollection("userConnections")
    ):
        return

    users = [
        User(
            usr="lpaone@systra.com",
            # psw sha256 of lpaone123456!
            psw="f8a50b3867de404e5164c297c9abe39a444d9605537d5656627cb3d6f6ff61f8",
            role=UserRole.USER,
            uuid=UUID("{e1176597-02e6-4859-99a4-83f96a88cbcd}"),
        ),
        User(
            usr="dmaturi@systra.com",
            # psw sha256 of dmaturi123456!
            psw="b902f245f52123cb8c908667e68dfa1c99200395de5b642d4d361e4b3953f286",
            role=UserRole.USER,
            uuid=UUID("{059302ab-e6ad-4a93-85c5-ffc655fd2a97}"),
        ),
        User(
            usr="user1@systra.com",
            # psw sha256 of user1123456!
            psw="52f1bc6e7fea0d4a18b65262cb5f4468dc1f51e589d13771e647f04b5683e719",
            role=UserRole.USER,
            uuid=uuid4(),
        ),
        User(
            usr="user2@systra.com",
            # psw sha256 of user2123456!
            psw="772dacd7e8eb806e48ce08754e473818c4b09c4ebb12adc5ad61f0bae06e746e",
            role=UserRole.USER,
            uuid=uuid4(),
        ),
        User(
            usr="user3@systra.com",
            # psw sha256 of user3123456!
            psw="ae4b7bc664659cd9b620a82352c2d0f1f4423b15e86863f66b95986555b18c18",
            role=UserRole.USER,
            uuid=uuid4(),
        ),
        User(
            usr="admin1@systra.com",
            # psw sha256 of admin1123456!
            psw="7dcf06eb47134617689951f266081883a89b2c23b69403213b641ffaf71ad862",
            role=UserRole.ADMIN,
            uuid=uuid4(),
        ),
        User(
            usr="admin2@systra.com",
            # psw sha256 of admin2123456!
            psw="824672e90c9f82c2c24482fc3b68be9a595212a959651209130ea9c940ab9755",
            role=UserRole.ADMIN,
            uuid=uuid4(),
        ),
        User(
            usr="admin3@systra.com",
            # psw sha256 of admin3123456!
            psw="f813ed390fcaa406765d182b543119f1b6d53843af6304e88bc06c0f2e7e0bc1",
            role=UserRole.ADMIN,
            uuid=uuid4(),
        ),
    ]
    pp = pprint.PrettyPrinter(indent=4)
    db.setCurrentCollection("users")

    for user in users:
        db.newDocument(user.dict())
        print(f"* Added a {user.role.value} with {user.usr}")
        pp.pprint(user.dict())


def userFindByUserName(userName: str) -> User:
    db = dbtools.DbManager()
    db.connect()
    db.setCurrentDb("swsmind")
    db.setCurrentCollection("users")
    id = db.findOne({"usr": userName})
    return User(**db.findById(id))


def userUpdate(user: User) -> bool:
    db = dbtools.DbManager()
    db.connect()
    db.setCurrentDb("swsmind")
    db.setCurrentCollection("users")
    db.findOne({"usr": user.usr})
    return db.replaceOne({"usr": user.usr}, user.dict())


def userChangePsw(usr: str, new_psw: str) -> bool:
    db = dbtools.DbManager()
    db.connect()
    db.setCurrentDb("swsmind")
    db.setCurrentCollection("users")
    id = db.findOne({"usr": usr})
    newUser = User(**db.findById(id))
    if not newUser.isNull():
        newUser.psw = new_psw
        return db.replaceOne({"usr": usr}, newUser.dict())
    else:
        return False


def userAdd(user: User) -> bool:
    db = dbtools.DbManager()
    db.connect()
    db.setCurrentDb("swsmind")
    db.setCurrentCollection("users")
    return db.newDocument(user.dict()) != ""


def userDel(usr: str) -> bool:
    db = dbtools.DbManager()
    db.connect()
    db.setCurrentDb("swsmind")
    db.setCurrentCollection("users")
    id = db.findOne({"usr": usr})
    return db.deleteById(id) > 0


def userFindByToken(token: UUID) -> User:
    db = dbtools.DbManager()
    db.connect()
    db.setCurrentDb("swsmind")
    db.setCurrentCollection("users")
    id = db.findOne({"uuid": token})
    return User(**db.findById(id))


def users() -> List[User]:
    db = dbtools.DbManager()
    db.connect()
    db.setCurrentDb("swsmind")
    db.setCurrentCollection("users")
    return db.getAllDocsFromCollection()


def printUsers():
    db = dbtools.DbManager()
    db.connect()
    db.setCurrentDb("swsmind")
    db.setCurrentCollection("users")
    db.printCollection()
