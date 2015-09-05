class AddFunction(MsgDef):
    pass

class GetSimilars(MsgDef):
    pass

class ResultSimilars(MsgDef):
    pass

class ChooseDB(MsgDef):
    pass


proto_def = {\
        0:AddFunction(),\
        1:GetSimilars(),\
        2:ChooseDB()}
