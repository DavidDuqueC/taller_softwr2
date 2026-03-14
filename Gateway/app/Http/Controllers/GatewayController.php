<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class GatewayController extends Controller
{

   public function getProductos()
    {
        $response = Http::withHeaders([
            'Authorization' => env('MICROSERVICES_API_KEY'),
        ])->get(env('FLASK_SERVICE_URL') . '/api/productos');

        return [
            'status' => $response->status(),
            'body' => $response->body(),
        ];
    }

 
    public function crearProducto(Request $request)
    {
        $response = Http::withHeaders([
            'Authorization' => env('MICROSERVICES_API_KEY'),
        ])->post(env('FLASK_SERVICE_URL') . '/api/productos', [
            'nombre' => $request->nombre,
            'descripcion' => $request->descripcion,
            'precio' => $request->precio,
            'stock' => $request->stock,
            'categoria' => $request->categoria,
        ]);

        return [
            'status' => $response->status(),
            'body' => $response->body(),
        ];
    }


    public function getVentas()
    {
        $response = Http::withHeaders([
            'Authorization' => env('MICROSERVICES_API_KEY'),
        ])->get(env('EXPRESS_SERVICE_URL') . '/api/ventas/');

        return [
            'status' => $response->status(),
            'body' => $response->body(),
        ];
    }


    public function crearVenta(Request $request)
    {
        $response = Http::withHeaders([
            'Authorization' => env('MICROSERVICES_API_KEY'),
        ])->post(env('EXPRESS_SERVICE_URL') . '/api/ventas/', [
            'usuarioId' => (string) auth()->id(),
            'usuarioEmail' => auth()->user()->email,
            'productos' => $request->productos,
            'metodoPago' => $request->metodoPago,
        ]);

        return [
            'status' => $response->status(),
            'body' => $response->body(),
        ];
    }


    public function vender(Request $request)
    {
        $productos = $request->productos;
        $metodoPago = $request->metodoPago;

        foreach ($productos as $producto) {
            $verificacion = Http::withHeaders([
                'Authorization' => env('MICROSERVICES_API_KEY'),
            ])->get(env('FLASK_SERVICE_URL') . '/api/productos/' . $producto['productoId'] . '/verificar-stock', [
                'cantidad' => $producto['cantidad']
            ]);

            $stockData = $verificacion->json();
            
            if (!$stockData['disponible']) {
                return [
                    'status' => 400,
                    'body' => json_encode([
                        'error' => 'Stock insuficiente',
                        'producto' => $producto['productoId']
                    ])
                ];
            }
        }

        $ventaResponse = Http::withHeaders([
            'Authorization' => env('MICROSERVICES_API_KEY'),
        ])->post(env('EXPRESS_SERVICE_URL') . '/api/ventas/', [
            'usuarioId' => (string) auth()->id(),
            'usuarioEmail' => auth()->user()->email,
            'productos' => $productos,
            'metodoPago' => $metodoPago,
        ]);

        if ($ventaResponse->failed()) {
            return [
                'status' => $ventaResponse->status(),
                'body' => $ventaResponse->body()
            ];
        }

        foreach ($productos as $producto) {
            Http::withHeaders([
                'Authorization' => env('MICROSERVICES_API_KEY'),
            ])->post(env('FLASK_SERVICE_URL') . '/api/productos/' . $producto['productoId'] . '/vender', [
                'cantidad' => $producto['cantidad']
            ]);
        }

        return [
            'status' => 201,
            'body' => $ventaResponse->body()
        ];
    }
}