from ninja import Router

router = Router(
    tags=["users"],
)


@router.get("/")
def test_api(request):
    return {"message": "Endpoint is working"}
