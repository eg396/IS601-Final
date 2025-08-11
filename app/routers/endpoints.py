# app/routers/endpoints.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationBase, CalculationResponse, CalculationUpdate
from app.database import get_db
from app.operations import add, subtract, multiply, divide

router = APIRouter(
    prefix="/calculations",
    tags=["calculations"]
)

# [B]READ

@router.get("/", response_model=list[CalculationResponse])
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).all()

# B[R]EAD

@router.get("/{calculation_id}", response_model=CalculationResponse)
def read_calculation(
    calculation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    return calc

# BR[E]AD

@router.put("/{calculation_id}", response_model=CalculationResponse)
@router.patch("/{calculation_id}", response_model=CalculationResponse)
def update_calculation(
    calculation_id: UUID,
    update_data: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    # Update the fields that were sent
    for field, value in update_data.model_dump(exclude_unset=True).items():

        setattr(calc, field, value)

    # If operands or operation changed, recalculate
    operation_map = {
        "addition": add,
        "subtraction": subtract,
        "multiplication": multiply,
        "division": divide
    }

    operation_key = getattr(calc, "type", None) or getattr(calc, "operation", None)

    if operation_key in operation_map:
        try:
            # Assuming inputs is a list with 2 values
            operand1, operand2 = calc.inputs
            calc.result = operation_map[operation_key](operand1, operand2)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")


    db.commit()
    db.refresh(calc)
    return calc

# BRE[A]D

@router.post("/", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED)
def add_calculation(
    calculation_data: CalculationBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    operation_map = {
        "addition": add,
        "subtraction": subtract,
        "multiplication": multiply,
        "division": divide
    }

    op_type = calculation_data.type.value

    if op_type not in operation_map:
        raise HTTPException(status_code=400, detail="Invalid operation")

    try:
        result = operation_map[op_type](calculation_data.inputs[0], calculation_data.inputs[1])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_calc = Calculation(
        user_id=current_user.id,
        type=calculation_data.type,
        inputs=calculation_data.inputs,
        result=result
    )

    db.add(new_calc)
    db.commit()
    db.refresh(new_calc)
    return new_calc

# BREA[D]

@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calculation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    db.delete(calc)
    db.commit()
    return None
