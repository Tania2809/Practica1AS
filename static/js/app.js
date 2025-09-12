function activeMenuOption(href) {
    $(".app-menu .nav-link")
        .removeClass("active")
        .removeAttr('aria-current')

    $(`[href="${(href ? href : "#/")}"]`)
        .addClass("active")
        .attr("aria-current", "page")
}

const app = angular.module("angularjsApp", ["ngRoute"])
app.config(function($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix("")

    $routeProvider
        .when("/", {
            templateUrl: "/app",
            controller: "appCtrl"
        })
        .when("/categorias", {
            templateUrl: "/categorias",
            controller: "categoriasCtrl"
        })
        .when("/lugares", {
            templateUrl: "/lugares",
            controller: "lugaresCtrl"
        })
        .when("/clientes", {
            templateUrl: "/clientes",
            controller: "clientesCtrl"
        })
        .when("/eventos", {
            templateUrl: "/eventos",
            controller: "eventosCtrl"
        })
        // Eliminé la ruta de productos ya que no está definida en tus controladores
        .otherwise({
            redirectTo: "/"
        })
})
app.run(["$rootScope", "$location", "$timeout", function($rootScope, $location, $timeout) {
    function actualizarFechaHora() {
        lxFechaHora = DateTime
            .now()
            .setLocale("es")

        $rootScope.angularjsHora = lxFechaHora.toFormat("hh:mm:ss a")
        $timeout(actualizarFechaHora, 1000)
    }

    $rootScope.slide = ""

    actualizarFechaHora()

    $rootScope.$on("$routeChangeSuccess", function(event, current, previous) {
        $("html").css("overflow-x", "hidden")


        const path = current.$$route.originalPath

        if (path.indexOf("splash") == -1) {
            const active = $(".app-menu .nav-link.active").parent().index()
            const click = $(`[href^="#${path}"]`).parent().index()

            if (active != click) {
                $rootScope.slide = "animate__animated animate__faster animate__slideIn"
                $rootScope.slide += ((active > click) ? "Left" : "Right")
            }

            $timeout(function() {
                $("html").css("overflow-x", "auto")

                $rootScope.slide = ""
            }, 1000)

            activeMenuOption(`#${path}`)
        }
    })
}])

app.controller("appCtrl", function($scope, $http) {})


app.controller("eventosCtrl", function($scope, $http) {

    $scope.eventos = []

    // Obtener lista de categorías
    $http.get("/eventos").then(function(res) {
        $scope.categorias = res.data
    })

    // Guardar evento
    $scope.guardar = function(eventos) {
        $http.post("/eventos/agregar", eventos).then(function(res) {
            console.log(res);
            console.log("evento guardado")
                // Recargar lista sin recargar toda la página
            $http.get("/eventos").then(function(res) {
                $scope.eventos = res.data
            })
            $scope.eventos = {} // Limpiar formulario
        }, function(err) {
            console.log("Error al guardar: " + (err.data ? err.message : ""));
        })
    }

    $scope.guardar = function(eventos) {
        $http.post("/eventos/eliminar", eventos).then(function(res) {
            console.log(res);
            console.log("evento eliminado")
                // Recargar lista sin recargar toda la página
            $http.get("/eventos").then(function(res) {
                $scope.eventos = res.data
            })
            $scope.eventos = {} // Limpiar formulario
        }, function(err) {
            console.log("Error al borrar: " + (err.data ? err.message : ""));
        })
    }


    // Obtener lista de eventos
    $http.get("/eventos").then(function(res) {
        $scope.eventos = res.data
    })

})


app.controller("categoriasCtrl", function($scope, $http) {
    $scope.categorias = [];
    $scope.mostrarTodos = true;

    // Configurar Pusher para tiempo real
    Pusher.logToConsole = true; // Activar logs para depuración
    var pusher = new Pusher("db840e3e13b1c007269e", {
        cluster: 'us2',
        encrypted: true
    });

    // Suscribirse al canal de categorías
    var channel = pusher.subscribe("canalCategorias");

    // Escuchar eventos de Pusher para actualizaciones en tiempo real
    channel.bind("categoria_guardada", function(data) {
        console.log('📦 Evento Pusher recibido: categoria_guardada', data);
        if ($scope.mostrarTodos) {
            $scope.allData(); // Recargar todos los datos
        }
        $scope.$applyAsync(); // Forzar actualización de Angular
    });

    channel.bind("categoria_eliminada", function(data) {
        console.log('📦 Evento Pusher recibido: categoria_eliminada', data);
        if ($scope.mostrarTodos) {
            $scope.allData(); // Recargar todos los datos
        }
        $scope.$applyAsync();
    });

    channel.bind("busqueda_realizada", function(data) {
        console.log('📦 Evento Pusher recibido: busqueda_realizada', data);
        // El backend podría notificar sobre búsquedas si es necesario
    });

    // Obtener todas las categorías
    $scope.allData = function() {
        $http.get("/categorias/all").then(function(res) {
            $("#tablaCategorias").html(res.data);
            console.log('✅ Datos cargados correctamente');
        }).catch(function(error) {
            console.error('❌ Error al cargar datos:', error);
            $("#tablaCategorias").html(`
                <tr>
                    <td colspan="4" class="text-center text-danger py-3">
                        <i class="fas fa-exclamation-triangle me-2"></i> 
                        Error al cargar categorías
                    </td>
                </tr>
            `);
        });
    };

    // Inicializa el template
    $http.get("/categorias").then(function(res) {
        $scope.allData();
    });

    // Guardar categoría - El backend publicará en Pusher automáticamente
    $scope.guardar = function(categoria) {
        if (!categoria.nombreCategoria || !categoria.nombreCategoria.trim()) {
            alert("El nombre de la categoría es requerido");
            return;
        }

        console.log('💾 Guardando categoría:', categoria);

        $http.post("/categorias/agregar", categoria)
            .then(function(response) {
                if (response.data.status === "success") {
                    $scope.categoria = {}; // Limpiar formulario
                    console.log('✅ Categoría guardada:', response.data);
                    alert("Categoría guardada correctamente");

                    // El backend se encarga de publicar el evento Pusher
                    // para que todos los usuarios reciban la actualización

                } else {
                    alert("Error: " + response.data.message);
                }
            })
            .catch(function(error) {
                console.error("❌ Error al guardar:", error);
                if (error.data && error.data.message) {
                    alert("Error: " + error.data.message);
                } else {
                    alert("Error desconocido al guardar la categoría");
                }
            });
    };

    // Buscar categorías
    $scope.buscar = function(nombre) {
        console.log("🔍 Buscando:", nombre);

        if (!nombre || nombre.trim() === '') {
            console.log("ℹ️ Búsqueda vacía, mostrando todos");
            $scope.mostrarTodos = true;
            $scope.allData();
            return;
        }

        $http.get("/categorias/buscar", {
                params: { busqueda: nombre }
            })
            .then(function(response) {
                $("#tablaCategorias").html(response.data);
                $scope.mostrarTodos = false;
                console.log('✅ Búsqueda completada');
            })
            .catch(function(error) {
                console.error("❌ Error en búsqueda:", error);

                let mensaje = "Error desconocido al buscar categorías";
                if (error.data && error.data.message) {
                    mensaje = error.data.message;
                } else if (error.status === 500) {
                    mensaje = "Error interno del servidor";
                }

                $("#tablaCategorias").html(`
                    <tr>
                        <td colspan="4" class="text-center text-danger py-3">
                            <i class="fas fa-exclamation-triangle me-2"></i> 
                            ${mensaje}
                        </td>
                    </tr>
                `);

                alert("Error en búsqueda: " + mensaje);
            });
    };

    // Limpiar búsqueda
    $scope.limpiarBusqueda = function() {
        $scope.nombre = '';
        $scope.mostrarTodos = true;
        $scope.allData();
        console.log('🔄 Búsqueda limpiada');
    };

    // Limpiar suscripciones cuando el controlador se destruye
    $scope.$on('$destroy', function() {
        console.log('🧹 Limpiando suscripciones de Pusher');
        pusher.unsubscribe("canalCategorias");
    });
});


app.controller("clientesCtrl", function($scope, $http) {
    $scope.clientes = []
    $scope.searching = false;
    $scope.allData = function() {
            $http.get("/clientes/all").then(function(res) {
                $("#tablaClientes").html(res.data)
            })
        }
        //inizializa el template
    $http.get("/clientes").then(function(res) {
        $scope.allData()
    })
    Pusher.logToConsole = true
    var pusher = new Pusher("db840e3e13b1c007269e", {
        cluster: 'us2'
    })
    var channel = pusher.subscribe("canalClientes");
    channel.bind("newDataInserted", function(data) {
        if (!$scope.searching)
            $scope.allData();
    })

    $scope.buscar = function(nombre) {
            if (!nombre || nombre.trim() === '') {
                $scope.searching = false
                $scope.allData(); // Si la búsqueda está vacía, mostrar todos
                return;
            }

            $http.get("/clientes/buscar", {
                params: {
                    busqueda: nombre
                }
            }).then(function(response) {
                console.log(response);

                $("#tablaClientes").html(response.data);
                $scope.searching = true;
            }, function(error) {
                console.error("Error en búsqueda:", error);
            })
        }
        // Guardar cliente
    $scope.guardar = function(cliente) {
        $http.post("/clientes/agregar", cliente).then(function() {
            $scope.cliente = {}
        }, function(err) {
            console.log("Error al guardar: " + (err.data ? err.message : ""))
        })
    }
})


app.controller("lugaresCtrl", function($scope, $http) {
    $scope.lugares = []

    $scope.allData = function() {
            $http.get("/lugares/all").then(function(res) {
                $("#tablaLugares").html(res.data)
            })
        }
        //inizializa el template
    $http.get("/").then(function(res) {
            $scope.allData()
            $http.get("/lugares/all").then(function(res) {
                $("#tablaLugares").html(res.data)
            })
        })
        //inizializa el template
    $http.get("/lugares").then(function(res) {
        $scope.allData()
    })

    Pusher.logToConsole = true

    var pusher = new Pusher("", {
        cluster: 'us2'
    })


    var channel = pusher.subscribe("");
    channel.bind("newDataInserted", function(data) {
        $scope.allData();
    })

    // Guardar lugar
    $scope.guardar = function(lugar) {
        $http.post("/lugar/guardar", lugar).then(function() {
            $scope.lugar = {}
            $scope.allData()
        }, function(err) {
            console.log("Error al guardar: " + (err.data ? err.message : ""))
        })
    }
})

const DateTime = luxon.DateTime
let lxFechaHora

document.addEventListener("DOMContentLoaded", function(event) {
    const configFechaHora = {
        locale: "es",
        weekNumbers: true,
        minuteIncrement: 15,
        altInput: true,
        altFormat: "d/F/Y",
        dateFormat: "Y-m-d",
    }

    activeMenuOption(location.hash)


})