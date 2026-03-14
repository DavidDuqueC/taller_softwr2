<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\GatewayController;

Route::post('register', [AuthController::class, 'register']);
Route::post('login', [AuthController::class, 'login']);

Route::middleware(['jwt.auth'])->group(function () {
    Route::post('logout', [AuthController::class, 'logout']);
    Route::get('me', [AuthController::class, 'me']);
    
    Route::get('productos', [GatewayController::class, 'getProductos']);
    Route::post('productos', [GatewayController::class, 'crearProducto']);
    
    Route::get('ventas', [GatewayController::class, 'getVentas']);
    Route::post('ventas', [GatewayController::class, 'crearVenta']);
    
    Route::post('vender', [GatewayController::class, 'vender']);
});