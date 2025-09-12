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



    // Guardar evento
    $scope.eliminar = function(evento) {
        $http.post("/eventos/eliminar", evento).then(function(res) {
            console.log(res);
            console.log("evento eliminado")
                // Recargar lista sin recargar toda la página
            $http.get("/eventos").then(function(res) {
                $scope.eventos = res.data
            })
            $scope.eventos = {} // Limpiar formulario
        }, function(err) {
            console.log("Error al guardar: " + (err.data ? err.message : ""));
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
    $scope.nombre = '';

    // Inicializar Pusher
    Pusher.logToConsole = true;
    var pusher = new Pusher("db840e3e13b1c007269e", {
        cluster: 'us2'
    });

    var channel = pusher.subscribe("canalCategorias");

    // Escuchar eventos de Pusher
    channel.bind("newDataInserted", function(data) {
        console.log('📢 Evento Pusher recibido: newDataInserted', data);
        if (!$scope.searching) {
            $scope.allData();
        }
        if (!$scope.$$phase) {
            $scope.$apply();
        }
    });

    // Obtener todas las categorías
    $scope.allData = function() {
        console.log('🔄 Cargando todas las categorías...');
        $http.get("/categorias/all")
            .then(function(res) {
                $("#tablaCategorias").html(res.data);
                console.log('✅ Tabla actualizada correctamente');
            })
            .catch(function(error) {
                console.error('❌ Error al cargar categorías:', error);
                $("#tablaCategorias").html(`
                    <tr>
                        <td colspan="3" class="text-center text-danger py-3">
                            <i class="fas fa-exclamation-triangle me-2"></i> 
                            Error al cargar categorías
                        </td>
                    </tr>
                `);
            });
    };

    // Inicializar
    $scope.inicializar = function() {
        $scope.allData();
    };

    // Iniciar
    $scope.inicializar();

    // Guardar categoría
    $scope.guardar = function(categoria) {
        if (!categoria || !categoria.nombreCategoria || !categoria.nombreCategoria.trim()) {
            alert("❌ El nombre de la categoría es requerido");
            return;
        }

        console.log('💾 Intentando guardar categoría:', categoria);

        $http.post("/categorias/agregar", categoria)
            .then(function(response) {
                console.log('✅ Respuesta del servidor:', response.data);
                if (response.data.status === "success") {
                    $scope.categoria = {}; // Limpiar formulario
                    alert("✅ Categoría guardada correctamente");
                    // Pusher se encargará de actualizar la tabla automáticamente
                } else {
                    alert("❌ Error: " + response.data.message);
                }
            })
            .catch(function(error) {
                console.error("❌ Error al guardar:", error);
                if (error.data && error.data.message) {
                    alert("❌ Error: " + error.data.message);
                } else {
                    alert("❌ Error desconocido al guardar la categoría");
                }
            });
    };

    // Buscar categorías
    $scope.buscar = function(nombre) {
        console.log("🔍 Buscando:", nombre);
        $scope.searching = true;

        if (!nombre || nombre.trim() === '') {
            $scope.mostrarTodos = true;
            $scope.searching = false;
            $scope.allData();
            return;
        }

        $http.get("/categorias/buscar", {
                params: { busqueda: nombre }
            })
            .then(function(response) {
                $("#tablaCategorias").html(response.data);
                $scope.mostrarTodos = false;
            })
            .catch(function(error) {
                console.error("❌ Error en búsqueda:", error);
                alert("Error en la búsqueda");
            });
    };

    // Limpiar búsqueda
    $scope.limpiarBusqueda = function() {
        $scope.nombre = '';
        $scope.mostrarTodos = true;
        $scope.searching = false;
        $scope.allData();
    };

    // Limpiar cuando se destruye el controlador
    $scope.$on('$destroy', function() {
        console.log('🧹 Desconectando Pusher...');
        pusher.unsubscribe("canalCategorias");
        pusher.disconnect();
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