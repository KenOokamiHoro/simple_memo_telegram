'''connect to backend database with SQLAlchemy'''
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm


class dbc:
    '''a datatbase connection.'''
    def __init__(self, uri):
        self.engine = sqlalchemy.create_engine(uri, echo=True)
        self.base = sqlalchemy.ext.declarative.declarative_base()
        self.Session = sqlalchemy.orm.sessionmaker()
        self.Session.configure(bind=self.engine)
        self.session = self.Session()

    def log_memo(self, channel, author, title, tag, memo):
        '''log a memo'''
        memo_item = ChatMemo(channel=channel, author=author, title=title, tag=tag, memo=memo)
        self.session.add(memo_item)
        self.session.commit()

    def Query(self,model):
        return self.session.query(model)
            
    def delete_memo(self,id):
        memo_item = self.Query(ChatMemo).filter_by(id=id).first()
        self.session.delete(memo_item)
        self.session.commit()

    def set_locale(self,user,locale):
        '''set a locale'''
        pass

class ChatMemo(sqlalchemy.ext.declarative.declarative_base()):
    '''memos model'''
    __tablename__ = 'memos'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    channel = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    title = sqlalchemy.Column(sqlalchemy.String(64), index=True)
    tag =  sqlalchemy.Column(sqlalchemy.String(64), index=True)
    memo = sqlalchemy.Column(sqlalchemy.Text())

    def jsonify(self):
        return {'id':self.id,'channel':self.channel,'author':self.author,
                'title':self.title,'tag':self.tag,'content':self.memo}

class User(sqlalchemy.ext.declarative.declarative_base()):
    '''users model'''
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    locale = sqlalchemy.Column(sqlalchemy.String(64), index=True)

def init(uri,*models):
    test_dbc = dbc(uri)
    for model in models:
        model.metadata.create_all(test_dbc.engine)

def usage():
    print("use --init after create configuration file :-)")

if __name__ == "__main__":
    try:
        import config,sys
        if "init" in sys.argv[1]:
            init(config.database,ChatMemo,User)
    except (ImportError,IndexError):
        usage()
        
