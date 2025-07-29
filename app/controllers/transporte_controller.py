from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import datetime, time
from app.database.connection import get_carelink_db as get_db
from app.models.transporte import CronogramaTransporte, EstadoTransporte
from app.models.attendance_schedule import CronogramaAsistenciaPacientes
from app.models.user import User
from app.dto.v1.request.transporte import CreateTransporteRequest, UpdateTransporteRequest
from app.dto.v1.response.transporte import (
    TransporteResponse, 
    CronogramaTransporteResponse,
    RutaDiariaResponse,
    RutaDiariaResponseWrapper,
    RutaTransporteResponse
)

router = APIRouter(prefix="/api/transporte", tags=["transporte"])

@router.post("/crear", response_model=TransporteResponse)
def crear_transporte(
    request: CreateTransporteRequest,
    db: Session = Depends(get_db)
):
    """Crear un nuevo registro de transporte"""
    try:
        # Verificar que el cronograma del paciente existe
        cronograma_paciente = db.query(CronogramaAsistenciaPacientes).filter(
            CronogramaAsistenciaPacientes.id_cronograma_paciente == request.id_cronograma_paciente
        ).first()
        
        if not cronograma_paciente:
            raise HTTPException(status_code=404, detail="Cronograma del paciente no encontrado")
        
        # Verificar que no existe ya un transporte para este cronograma
        transporte_existente = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_cronograma_paciente == request.id_cronograma_paciente
        ).first()
        
        if transporte_existente:
            raise HTTPException(status_code=400, detail="Ya existe un transporte para este cronograma")
        
        # Convertir horarios a objetos time
        hora_recogida = None
        hora_entrega = None
        
        if request.hora_recogida:
            try:
                hora_recogida = datetime.strptime(request.hora_recogida, "%H:%M:%S").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora de recogida inválido")
        
        if request.hora_entrega:
            try:
                hora_entrega = datetime.strptime(request.hora_entrega, "%H:%M:%S").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora de entrega inválido")
        
        # Crear el transporte
        nuevo_transporte = CronogramaTransporte(
            id_cronograma_paciente=request.id_cronograma_paciente,
            direccion_recogida=request.direccion_recogida,
            direccion_entrega=request.direccion_entrega,
            hora_recogida=hora_recogida,
            hora_entrega=hora_entrega,
            estado=EstadoTransporte.PENDIENTE,
            observaciones=request.observaciones
        )
        
        db.add(nuevo_transporte)
        db.commit()
        db.refresh(nuevo_transporte)
        
        # Actualizar el campo requiere_transporte en el cronograma
        cronograma_paciente.requiere_transporte = True
        db.commit()
        
        return TransporteResponse(
            message="Transporte creado exitosamente",
            data=CronogramaTransporteResponse.from_orm(nuevo_transporte)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.patch("/{id_transporte}/horarios", response_model=TransporteResponse)
def actualizar_horarios_transporte(
    id_transporte: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """Actualizar solo las horas de recogida y entrega de un transporte"""
    try:
        transporte = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_transporte == id_transporte
        ).first()
        
        if not transporte:
            raise HTTPException(status_code=404, detail="Transporte no encontrado")
        
        # Convertir horarios
        if 'hora_recogida' in request and request['hora_recogida'] is not None:
            try:
                transporte.hora_recogida = datetime.strptime(request['hora_recogida'], "%H:%M:%S").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora de recogida inválido")
        
        if 'hora_entrega' in request and request['hora_entrega'] is not None:
            try:
                transporte.hora_entrega = datetime.strptime(request['hora_entrega'], "%H:%M:%S").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora de entrega inválido")
        
        db.commit()
        db.refresh(transporte)
        
        return TransporteResponse(
            message="Horarios de transporte actualizados exitosamente",
            data=CronogramaTransporteResponse.from_orm(transporte)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.patch("/{id_transporte}", response_model=TransporteResponse)
def actualizar_transporte(
    id_transporte: int,
    request: UpdateTransporteRequest,
    db: Session = Depends(get_db)
):
    """Actualizar un registro de transporte"""
    try:
        transporte = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_transporte == id_transporte
        ).first()
        
        if not transporte:
            raise HTTPException(status_code=404, detail="Transporte no encontrado")
        
        # Actualizar campos
        if request.direccion_recogida is not None:
            transporte.direccion_recogida = request.direccion_recogida
        if request.direccion_entrega is not None:
            transporte.direccion_entrega = request.direccion_entrega
        if request.observaciones is not None:
            transporte.observaciones = request.observaciones
        if request.estado is not None:
            try:
                transporte.estado = EstadoTransporte(request.estado)
            except ValueError:
                raise HTTPException(status_code=400, detail="Estado inválido")
        
        # Convertir horarios
        if request.hora_recogida is not None:
            try:
                transporte.hora_recogida = datetime.strptime(request.hora_recogida, "%H:%M:%S").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora de recogida inválido")
        
        if request.hora_entrega is not None:
            try:
                transporte.hora_entrega = datetime.strptime(request.hora_entrega, "%H:%M:%S").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora de entrega inválido")
        
        db.commit()
        db.refresh(transporte)
        
        return TransporteResponse(
            message="Transporte actualizado exitosamente",
            data=CronogramaTransporteResponse.from_orm(transporte)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/ruta/{fecha}", response_model=RutaDiariaResponseWrapper)
def obtener_ruta_diaria(
    fecha: str,
    db: Session = Depends(get_db)
):
    """Obtener TODOS los transportes para una fecha específica (sin filtros por profesional)"""
    try:
        # Convertir fecha
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Obtener TODOS los cronogramas para la fecha (sin filtrar por profesional)
        cronograma = db.query(CronogramaAsistenciaPacientes).join(
            CronogramaAsistenciaPacientes.cronograma
        ).filter(
            and_(
                CronogramaAsistenciaPacientes.cronograma.has(fecha=fecha_obj),
                CronogramaAsistenciaPacientes.requiere_transporte == True
            )
        ).all()
        
        # Obtener información de transporte para cada paciente
        rutas = []
        for paciente in cronograma:
            transporte = db.query(CronogramaTransporte).filter(
                CronogramaTransporte.id_cronograma_paciente == paciente.id_cronograma_paciente
            ).first()
            
            if transporte:
                # Obtener información del usuario
                usuario = db.query(User).filter(
                    User.id_usuario == paciente.id_usuario
                ).first()
                
                if usuario:
                    ruta = RutaTransporteResponse(
                        id_transporte=transporte.id_transporte,
                        id_cronograma_paciente=paciente.id_cronograma_paciente,
                        nombres=usuario.nombres,
                        apellidos=usuario.apellidos,
                        n_documento=usuario.n_documento,
                        direccion_recogida=usuario.direccion,  # Usar dirección del usuario
                        telefono_contacto=usuario.telefono,    # Agregar teléfono del usuario
                        hora_recogida=str(transporte.hora_recogida) if transporte.hora_recogida else None,
                        hora_entrega=str(transporte.hora_entrega) if transporte.hora_entrega else None,
                        estado=transporte.estado.value,
                        observaciones=transporte.observaciones
                    )
                    rutas.append(ruta)
        
        # Calcular estadísticas
        total_pacientes = len(rutas)
        total_pendientes = len([r for r in rutas if r.estado == "PENDIENTE"])
        total_realizados = len([r for r in rutas if r.estado == "REALIZADO"])
        total_cancelados = len([r for r in rutas if r.estado == "CANCELADO"])
        
        ruta_diaria = RutaDiariaResponse(
            fecha=fecha,
            total_pacientes=total_pacientes,
            total_pendientes=total_pendientes,
            total_realizados=total_realizados,
            total_cancelados=total_cancelados,
            rutas=rutas
        )
        
        return RutaDiariaResponseWrapper(data=ruta_diaria)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/paciente/{id_cronograma_paciente}", response_model=TransporteResponse)
def obtener_transporte_paciente(
    id_cronograma_paciente: int,
    db: Session = Depends(get_db)
):
    """Obtener información de transporte de un paciente específico"""
    try:
        transporte = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_cronograma_paciente == id_cronograma_paciente
        ).first()
        
        if not transporte:
            raise HTTPException(status_code=404, detail="Transporte no encontrado para este paciente")
        
        return TransporteResponse(
            message="Transporte obtenido exitosamente",
            data=CronogramaTransporteResponse.from_orm(transporte)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/{id_transporte}")
def eliminar_transporte(
    id_transporte: int,
    db: Session = Depends(get_db)
):
    """Eliminar un registro de transporte"""
    try:
        transporte = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_transporte == id_transporte
        ).first()
        
        if not transporte:
            raise HTTPException(status_code=404, detail="Transporte no encontrado")
        
        # Actualizar el campo requiere_transporte en el cronograma
        cronograma_paciente = db.query(CronogramaAsistenciaPacientes).filter(
            CronogramaAsistenciaPacientes.id_cronograma_paciente == transporte.id_cronograma_paciente
        ).first()
        
        if cronograma_paciente:
            cronograma_paciente.requiere_transporte = False
        
        db.delete(transporte)
        db.commit()
        
        return {"success": True, "message": "Transporte eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}") 