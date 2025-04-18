from fastapi import APIRouter

router = APIRouter()

@router.get("/trigger/test/1")
def trigger_test():
  message = "Tá rodando tudo certinho na fase 1"
  status = 200
  return {"message": message, "status_code": status}

@router.get("/trigger/test/2")
def trigger_test_2():
  message = "Tá rodando tudo certinho na fase 2"
  status = 200
  return {"message": message, "status_code": status}

@router.get("/trigger/test/3")
def trigger_test_3():
  message = "Tá rodando tudo certinho na fase 3"
  status = 200
  return {"message": message, "status_code": status}
