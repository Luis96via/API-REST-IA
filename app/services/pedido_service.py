from typing import Dict, Any, List, Optional
from app.services.db_service import db_service
from app.exceptions import DatabaseError, ValidationError

class PedidoService:
    """Servicio para manejar las operaciones relacionadas con pedidos"""
    
    async def crear_pedido(self, usuario_id: int, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crea un nuevo pedido y actualiza el stock de los productos.
        
        Args:
            usuario_id: ID del usuario que realiza el pedido
            items: Lista de items del pedido, cada uno con:
                  - producto_id: ID del producto
                  - cantidad: Cantidad solicitada
                  
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Validar que hay items en el pedido
            if not items:
                raise ValidationError("El pedido debe contener al menos un item")
            
            # Calcular el total y validar stock
            total = 0
            with db_service._get_connection() as conn:
                with conn.cursor() as cur:
                    # Iniciar transacción
                    cur.execute("BEGIN")
                    
                    try:
                        # Verificar stock y calcular total
                        for item in items:
                            producto_id = item['producto_id']
                            cantidad = item['cantidad']
                            
                            # Verificar stock disponible
                            cur.execute("""
                                SELECT precio, stock 
                                FROM productos 
                                WHERE id = %s FOR UPDATE
                            """, (producto_id,))
                            
                            producto = cur.fetchone()
                            if not producto:
                                raise ValidationError(f"Producto {producto_id} no encontrado")
                            
                            if producto['stock'] < cantidad:
                                raise ValidationError(
                                    f"Stock insuficiente para el producto {producto_id}. "
                                    f"Disponible: {producto['stock']}, Solicitado: {cantidad}"
                                )
                            
                            # Actualizar stock
                            cur.execute("""
                                UPDATE productos 
                                SET stock = stock - %s,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE id = %s
                            """, (cantidad, producto_id))
                            
                            # Acumular total
                            total += producto['precio'] * cantidad
                        
                        # Crear el pedido
                        cur.execute("""
                            INSERT INTO pedidos (usuario_id, total, estado)
                            VALUES (%s, %s, 'pendiente')
                            RETURNING id
                        """, (usuario_id, total))
                        
                        pedido_id = cur.fetchone()['id']
                        
                        # Crear detalles del pedido
                        for item in items:
                            producto_id = item['producto_id']
                            cantidad = item['cantidad']
                            
                            cur.execute("""
                                INSERT INTO detalles_pedido 
                                    (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                                SELECT 
                                    %s, 
                                    %s, 
                                    %s, 
                                    precio, 
                                    precio * %s
                                FROM productos 
                                WHERE id = %s
                            """, (pedido_id, producto_id, cantidad, cantidad, producto_id))
                        
                        # Confirmar transacción
                        conn.commit()
                        
                        return {
                            "status": "success",
                            "message": "Pedido creado exitosamente",
                            "pedido_id": pedido_id,
                            "total": total
                        }
                        
                    except Exception as e:
                        # Si hay error, revertir cambios
                        conn.rollback()
                        raise e
                        
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Error al crear el pedido: {str(e)}")

# Instancia global del servicio de pedidos
pedido_service = PedidoService() 