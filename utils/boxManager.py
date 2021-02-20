import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.datastructures import FileStorage
from empty import BoxBase, MetaDataBase
from empty.BoxEmpty import Box, BoxKey
from sqlalchemy.orm.session import Session
from empty.MetaDataEmpty import create_MetaData
from utils import cf
from sqlalchemy.pool import SingletonThreadPool, QueuePool, NullPool

dbconfig = {x[0]: x[1] for x in cf.items(section="db")}
mysql_conn = dbconfig.get("jdbc")


def makedirs(path):
    if os.path.exists(path) and os.path.isdir(path):
        return
    else:
        try:
            os.makedirs(path)
        except:
            return


class BoxManager():
    def __init__(self):
        self.main_engine =  create_engine(mysql_conn, echo=False,pool_recycle=True,pool_size=100,max_overflow=100)
        # self.main_engine = create_engine(mysql_conn, echo=False, poolclass=NullPool)
        BoxBase.metadata.create_all(self.main_engine, checkfirst=True)
        self.BoxSessionMaker = scoped_session(sessionmaker(bind=self.main_engine))
        self.MetaMap = dict()
        self.metadata_warning = [x[1] for x in cf.items(section="metadata_warning")]
        self.init_boxs()

    def getBoxSession(self) -> Session:
        res = self.BoxSessionMaker()
        # print("当前连接数：", self.main_engine.pool._pool.qsize())
        return res

    def init_box(self, path):
        makedirs(path)
        for warning in self.metadata_warning:
            makedirs(os.path.join(path, warning))
        path = os.path.join(path, "metadata.db")
        # metadata_engine = create_engine('sqlite:///%s?check_same_thread=False' % path, echo=False)

    def flush_engine(self):
        self.metadata_engine = create_engine(mysql_conn, echo=False,pool_recycle=True,pool_size=100,max_overflow=100)
        # self.metadata_engine = create_engine(mysql_conn, echo=False, poolclass=NullPool)
        # QueuePool
        MetaDataBase.metadata.create_all(self.metadata_engine, checkfirst=True)
        self.MetaSessionMaker = scoped_session(sessionmaker(bind=self.metadata_engine))

    def init_boxs(self):
        boxSession = self.getBoxSession()
        for _ in boxSession.query(Box).all():
            _: Box
            if _.enable:
                self.MetaMap.update({
                    _.box_id: create_MetaData(_.box_id)
                })
                self.init_box(_.box_path)
                print("初始化`%s`完成" % _.box_name)
        boxSession.close()
        self.flush_engine()

    def get_box_info_by_all(self):
        res = []
        boxSession = self.getBoxSession()
        for _ in boxSession.query(Box).filter_by(v_del=False).all():
            _: dict = _.to_dict()
            _.update({
                "keys": [_.to_dict() for _ in boxSession.query(BoxKey).filter_by(box_id=_.get("box_id")).all()]
            })
            res.append(_)
        boxSession.close()
        return res

    def get_box_by_id(self, box_id) -> Box:
        boxSession = self.getBoxSession()
        res = boxSession.query(Box).filter_by(box_id=box_id).first()
        boxSession.close()
        return res

    def get_box_by_key_id(self, key_id) -> Box:
        key = self.get_key_by_id(key_id)
        boxSession = self.getBoxSession()
        res = boxSession.query(Box).filter_by(box_id=key.box_id).first()
        boxSession.close()
        return res

    def get_metadata_session(self, box_id) -> Session:
        MetaData = self.MetaMap.get(box_id, None)
        # print(self.metadata_engine.pool._pool.qsize())
        if MetaData:
            return self.MetaSessionMaker()
        else:
            box: Box = self.get_box_by_id(box_id)
            self.MetaMap.update({
                box.box_id: create_MetaData(box.box_id)
            })
            self.flush_engine()
            return self.MetaSessionMaker()

    def get_key_by_id(self, key_id) -> BoxKey:
        boxSession = self.getBoxSession()
        res = boxSession.query(BoxKey).filter_by(key_id=key_id).first()
        boxSession.close()
        return res

    def get_keys_by_box_id(self, box_id) -> list:
        boxSession = self.getBoxSession()
        res = [_.to_dict() for _ in boxSession.query(BoxKey).filter_by(box_id=box_id).all()]
        boxSession.close()
        return res

    def get_keys_count_by_box_id(self, box_id) -> int:
        boxSession = self.getBoxSession()
        res = boxSession.query(BoxKey).filter_by(box_id=box_id).count()
        boxSession.close()
        return res

    def get_metadata_list_By_box_id(self, box_id) -> list:
        mdSession = self.get_metadata_session(box_id)
        MetaData = self.MetaMap.get(box_id)
        res = [_.to_dict() for _ in mdSession.query(MetaData).all()]
        mdSession.close()
        return res

    def get_metadata_dir_list_By_box_id(self, box_id, file_path, page=1, limit=10) -> list:
        mdSession = self.get_metadata_session(box_id)
        MetaData = self.MetaMap.get(box_id)
        if file_path == "" or file_path is None:
            res = [{"thumb": "",
                    "type": "directory",
                    "path": _[0],
                    "name": _[0],
                    } for _ in
                   mdSession.query(MetaData.file_path, func.count(MetaData.file_path))
                       .filter_by(v_del=False).group_by(
                       MetaData.file_path).offset((page - 1) * limit).limit(limit).all()]
            mdSession.close()
            return res
        else:
            res = [{"thumb": "/file_box/file/%s/%s" % (box_id, _.file_id),
                    "type": str(_.file_suffix).replace(".", ""),
                    "path": _.file_path,
                    "name": _.file_old_name,
                    "file_id": _.file_id,
                    } for _ in
                   mdSession.query(MetaData).filter_by(file_path=file_path)
                       .offset((page - 1) * limit).limit(limit).all()]
            mdSession.close()
            return res

    def get_metadata_dir_count_By_box_id(self, box_id, file_path) -> list:
        mdSession = self.get_metadata_session(box_id)
        MetaData = self.MetaMap.get(box_id)
        if file_path == "" or file_path is None:
            res = mdSession.query(MetaData.file_path).filter_by(v_del=False).group_by(
                MetaData.file_path).count()
            mdSession.close()
            return res
        else:
            res = mdSession.query(MetaData).filter_by(file_path=file_path).count()
            mdSession.close()
            return res

    def get_metadata_By_rel(self, box_id, rel):
        mdSession = self.get_metadata_session(box_id)
        MetaData = self.MetaMap.get(box_id)
        res = mdSession.query(MetaData).filter_by(rel=rel).first()
        mdSession.close()
        return res

    def get_metadata_By_file_id(self, box_id, file_id):
        mdSession = self.get_metadata_session(box_id)
        MetaData = self.MetaMap.get(box_id)
        res = mdSession.query(MetaData).filter_by(file_id=file_id).first()
        mdSession.close()
        return res

    def key_is_exists(self, key_id) -> bool:
        boxSession = self.getBoxSession()
        res = boxSession.query(BoxKey).filter_by(key_id=key_id).count() >= 1
        boxSession.close()
        return res

    def box_is_exists(self, box_id) -> bool:
        boxSession = self.getBoxSession()
        res = boxSession.query(Box).filter_by(box_id=box_id).count() >= 1
        boxSession.close()
        return res

    def file_is_exists_by_rel_id(self, key_id, rel_id) -> bool:
        box: Box = self.get_box_by_key_id(key_id)
        mdSession = self.get_metadata_session(box.box_id)
        MetaData = self.MetaMap.get(box.box_id)
        res = mdSession.query(MetaData).filter_by(rel=rel_id).count() >= 1
        mdSession.close()
        return res

    def file_is_exists_by_file_id(self, key_id, file_id) -> bool:
        box: Box = self.get_box_by_key_id(key_id)
        mdSession = self.get_metadata_session(box.box_id)
        MetaData = self.MetaMap.get(box.box_id)
        res = mdSession.query(MetaData).filter_by(file_id=file_id).count() >= 1
        mdSession.close()
        return res

    def key_is_readable(self, key_id) -> bool:
        boxSession = self.getBoxSession()
        res = boxSession.query(BoxKey).filter_by(key_id=key_id, read_perm=True).count() >= 1
        boxSession.close()
        return res

    def key_is_writable(self, key_id) -> bool:
        boxSession = self.getBoxSession()
        res = boxSession.query(BoxKey).filter_by(key_id=key_id, write_perm=True).count() >= 1
        boxSession.close()
        return res

    def box_is_enable(self, key_id) -> bool:
        boxSession = self.getBoxSession()
        res = boxSession.query(Box).filter_by(box_id=self.get_key_by_id(key_id).box_id,
                                              enable=True).count() >= 1
        boxSession.close()
        return res

    def save_file_by_box_id(self, key_id: str, file: FileStorage, cus_id: str, label: str, filename: str) -> dict:
        box: Box = self.get_box_by_key_id(key_id)
        mdSession = self.get_metadata_session(box.box_id)
        MetaData = self.MetaMap.get(box.box_id)
        _data = datetime.now()
        file_id = str(uuid.uuid4())
        file_old_name = file.filename
        file_read = file.read()
        file_size = len(file_read)
        file_path = _data.strftime("%Y\\%m\\%d")
        file_suffix = str(os.path.splitext(file_old_name)[-1]).lower()
        print(filename)
        if not filename == "" and filename is not None:
            file_old_name = filename
        file_name = file_id + file_suffix
        # file_name = str(os.path.splitext(file_old_name)[1])
        save_dir_path = os.path.join(box.box_path, file_path)
        save_file_path = os.path.join(box.box_path, file_path, file_name)
        makedirs(save_dir_path)
        with open(save_file_path, mode="wb") as wb:
            wb.write(file_read)
        mdSession.add(MetaData(
            file_id=file_id,
            file_path=file_path,
            file_name=file_name,
            file_old_name=file_old_name,
            file_suffix=file_suffix,
            file_size=file_size,
            rel=cus_id,
            label=label,
            v_del=False,
        ))
        mdSession.commit()
        mdSession.close()
        return {
            "file_id": file_id,
            "rel": cus_id,
            "index": label
        }

    def file_size(self, bi):
        i = 0
        iv = ['B', 'KB', 'MB', 'GB', 'TB']
        while (True):
            if bi // 1024 <= 0:
                return str(bi) + iv[i]
            bi = round(bi / 1024, 2)
            i += 1

    def get_file_info_by_file_key_id(self, key_id, file_id) -> dict:
        box: Box = self.get_box_by_key_id(key_id)
        md = self.get_metadata_By_file_id(box.box_id, file_id)
        file_path = os.path.join(box.box_path, md.file_path, md.file_name)
        return {
            "file_path": file_path,
            "file_name": md.file_old_name,
            "file_type": str(md.file_suffix).replace(".", ""),
            "file_size": self.file_size(md.file_size),
            "file_url": "/file_box/file/%s/%s" % (box.box_id, md.file_id),
            "file_gateway": "/gateway/download/by_id/%s/%s" % (key_id, md.file_id),
        }

    def get_file_info_by_rel_key_id(self, key_id, rel_id) -> dict:
        box: Box = self.get_box_by_key_id(key_id)
        md = self.get_metadata_By_rel(box.box_id, rel_id)
        file_path = os.path.join(box.box_path, md.file_path, md.file_name)
        return {
            "file_path": file_path,
            "file_name": md.file_old_name,
            "file_type": str(md.file_suffix).replace(".", ""),
            "file_size": self.file_size(md.file_size),
            "file_url": "/file_box/file/%s/%s" % (box.box_id, md.file_id),
            "file_gateway": "/gateway/download/by_id/%s/%s" % (key_id, md.file_id),
        }

    def get_file_info_by_file_box_id(self, box_id, file_id) -> dict:
        box: Box = self.get_box_by_id(box_id)
        md = self.get_metadata_By_file_id(box.box_id, file_id)
        file_path = os.path.join(box.box_path, md.file_path, md.file_name)
        return {
            "file_path": file_path,
            "file_name": md.file_old_name,
            "file_type": str(md.file_suffix).replace(".", ""),
            "file_size": self.file_size(md.file_size),
            "file_url": "/file_box/file/%s/%s" % (box.box_id, md.file_id)
        }

    def get_file_info_by_rel_box_id(self, box_id, rel_id) -> dict:
        box: Box = self.get_box_by_id(box_id)
        md = self.get_metadata_By_rel(box.box_id, rel_id)
        file_path = os.path.join(box.box_path, md.file_path, md.file_name)
        return {
            "file_path": file_path,
            "file_name": md.file_old_name,
            "file_type": str(md.file_suffix).replace(".", ""),
            "file_size": self.file_size(md.file_size),
            "file_url": "/file_box/file/%s/%s" % (box.box_id, md.file_id)
        }

    def get_file_list_by_key_id(self, key_id, index) -> list:
        mdSession = self.get_metadata_session(self.get_box_by_key_id(key_id).box_id)
        MetaData = self.MetaMap.get(self.get_box_by_key_id(key_id).box_id)
        if index == "" or index is None:
            res = mdSession.query(MetaData).filter_by(v_del=False).all()
        else:
            res = mdSession.query(MetaData).filter_by(v_del=False, label=index).all()
        mdSession.close()
        return [{
            "file_name": _.file_old_name,
            "file_size": self.file_size(_.file_size),
            "file_suffix": str(_.file_suffix).replace(".", ""),
            "index": _.label,
            "rel": _.rel,
            "id": _.file_id
        } for _ in res]

    def del_file_by_id(self, key_id, file_id, index):
        mdSession = self.get_metadata_session(self.get_box_by_key_id(key_id).box_id)
        MetaData = self.MetaMap.get(self.get_box_by_key_id(key_id).box_id)
        if (index is not None and not index == ""):
            mdSession.query(MetaData).filter_by(label=index).update({
                "v_del": True
            })
        else:
            mdSession.query(MetaData).filter_by(file_id=file_id).update({
                "v_del": True
            })
        mdSession.commit()
        mdSession.close()

    def del_file_by_rel(self, key_id, rel, index):
        mdSession = self.get_metadata_session(self.get_box_by_key_id(key_id).box_id)
        MetaData = self.MetaMap.get(self.get_box_by_key_id(key_id).box_id)
        if (index is not None and not index == ""):
            mdSession.query(MetaData).filter_by(label=index).update({
                "v_del": True
            })
        else:
            mdSession.query(MetaData).filter_by(rel=rel).update({
                "v_del": True
            })
        mdSession.commit()
        mdSession.close()
