function activeMenuOption(href) {
    $(".app-menu .nav-link")
        .removeClass("active")
        .removeAttr('aria-current')

    $(`[href="${(href ? href : "#/")}"]`)
        .addClass("active")
        .attr("aria-current", "page")
}

const app = angular.module("angularjsApp", ["ngRoute"])
app.config(function ($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix("")

    $routeProvider
        .when("/", {
            templateUrl: "/loginView",
            controller: "loginCtrl"
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

app.run(["$rootScope", "$location", "$timeout", function ($rootScope, $location, $timeout) {

    function actualizarFechaHora() {
        lxFechaHora = DateTime
            .now()
            .setLocale("es")

        $rootScope.angularjsHora = lxFechaHora.toFormat("hh:mm:ss a")
        $timeout(actualizarFechaHora, 1000)
    }

    $rootScope.slide = ""
    $rootScope.login = false
    actualizarFechaHora()
    $rootScope.$on('$routeChangeStart', function (event, next, current) {


        if ($rootScope.login == false) {
            if (next != null && next.$$route.originalPath != "/")
                $location.path("/")

        }


    })
    $rootScope.$on("$routeChangeSuccess", function (event, current, previous) {
        $("html").css("overflow-x", "hidden")


        const path = current.$$route.originalPath

        if (path.indexOf("splash") == -1) {
            const active = $(".app-menu .nav-link.active").parent().index()
            const click = $(`[href^="#${path}"]`).parent().index()

            if (active != click) {
                $rootScope.slide = "animate__animated animate__faster animate__slideIn"
                $rootScope.slide += ((active > click) ? "Left" : "Right")
            }

            $timeout(function () {
                $("html").css("overflow-x", "auto")

                $rootScope.slide = ""
            }, 1000)

            activeMenuOption(`#${path}`)
        }
    })
}])

app.controller("loginCtrl", ["$scope", "$rootScope", "$http", "$timeout", "$location",
    function ($scope, $rootScope, $http, $timeout, $location) {
        // Inicializar el modelo de datos
        $scope.userData = {
            username: '',
            password: ''
        };

        // Función para manejar el envío del formulario
        $scope.submitLogin = function () {
            // Aquí procesarías los datos de inicio de sesión
       
            $http.post("/login", $scope.userData).then(function (res) {
              

                if (res.data == 1) {

                    // Redirigimos después de un breve retraso
                    $timeout(function () {
                        // Usamos $location para cambiar la ruta en lugar de window.location
                        $location.path("/eventos");
                        $rootScope.login = true;
                    }, 2000);
                }
            });
        };
    }]);
app.controller("eventosCtrl", function ($scope, $http, $compile) {

    $scope.eventos = []

    $scope.agregarAngularATemplate = function (data) {
        var compiled = $compile(data)($scope);
        angular.element('#tablaEventos').html(compiled);
    }

    // Cargar datos de eventos
    $scope.cargarEventos = function () {
        $http.get("/eventos/all").then(function (res) {
            $scope.agregarAngularATemplate(res.data);
        });
    };
    //inizializa el template
    $scope.$on('$viewContentLoaded', function () {
        $scope.cargarEventos()
    });


    Pusher.logToConsole = true
    var pusher = new Pusher("db840e3e13b1c007269e", {
        cluster: 'us2'
    })
    var channel = pusher.subscribe("canalEventos");
    channel.bind("newDataInserted", function (data) {
        $scope.cargarEventos();
    })

    // Guardar evento
    $scope.guardar = function (eventos) {
        $http.post("/eventos/agregar", eventos).then(function (res) {
    

            $scope.eventos = {} // Limpiar formulario
        }, function (err) {
            console.log("Error al guardar: " + (err.data ? err.message : ""));
        })
    }

    // eliminar evento
    $scope.eliminar = function (evento) {
  

        $http.post("/eventos/eliminar", evento).then(function (res) {
        

            $scope.evento = {} // Limpiar formulario
        }, function (err) {
            console.log("Error al eliminar: " + (err.data ? err.message : ""));
        })
    }

    $scope.cargarEventos()
})

app.controller("categoriasCtrl", function ($scope, $http) {
    $scope.categorias = [];
    $scope.mostrarTodos = true;

    // Inicializar el bus de eventos
    const eventBus = {
        subscribers: {},

        subscribe: function (eventName, callback) {
            if (!this.subscribers[eventName]) {
                this.subscribers[eventName] = [];
            }
            this.subscribers[eventName].push(callback);
        },

        publish: function (eventName, data) {
            if (this.subscribers[eventName]) {
                this.subscribers[eventName].forEach(callback => {
                    callback(data);
                });
            }
        }
    };

    // Servicio de Categorías
    const categoriaService = {
        cargarTodas: function () {
            return $http.get("/categorias/all").then(function (res) {
                $("#tablaCategorias").html(res.data);
                eventBus.publish('categorias_actualizadas', res.data);
                return res.data;
            });
        },

        buscar: function (nombre) {
            return $http.get("/categorias/buscar", {
                params: { busqueda: nombre }
            }).then(function (response) {
                $("#tablaCategorias").html(response.data);
                eventBus.publish('busqueda_realizada', response.data);
                return response.data;
            });
        },

        guardar: function (categoria) {
            return $http.post("/categorias/agregar", categoria);
        }
    };

    // Servicio de Notificaciones
    const notificacionService = {
        init: function () {
            eventBus.subscribe('categoria_guardada', function (data) {
             //   console.log('Notificación: Categoría guardada exitosamente', data);
            });

            eventBus.subscribe('error_guardado', function (error) {
             //   console.error('Notificación: Error al guardar categoría', error);
            });

            eventBus.subscribe('evento_pusher_recibido', function (data) {
            //    console.log('Notificación: Cambios en tiempo real recibidos', data);
            });
        }
    };

    // Servicio de Analytics
    const analyticsService = {
        init: function () {
            eventBus.subscribe('busqueda_realizada', function (data) {
            //    console.log('Analytics: Búsqueda realizada', data);
            });

            eventBus.subscribe('categoria_guardada', function (data) {
            //    console.log('Analytics: Nueva categoría creada', data);
            });
        }
    };

    // Servicio de Pusher
    const pusherService = {
        init: function () {
            Pusher.logToConsole = true;
            var pusher = new Pusher("db840e3e13b1c007269e", {
                cluster: 'us2',
                encrypted: true
            });

            var channel = pusher.subscribe("canalCategorias");
            channel.bind("newDataInserted", function (data) {
           
                eventBus.publish('evento_pusher_recibido', data);

                if ($scope.mostrarTodos) {
                    categoriaService.cargarTodas();
                } else {
                    $scope.buscar($scope.nombre);
                }
            });

            channel.bind('pusher:subscription_error', function (status) {
                console.error('Error de suscripción Pusher:', status);
            });
        }
    };

    // Inicializar todos los servicios
    notificacionService.init();
    analyticsService.init();
    pusherService.init();

    // Cargar datos iniciales
    categoriaService.cargarTodas();

    // Guardar categoría
    $scope.guardar = function (categoria) {
        categoriaService.guardar(categoria)
            .then(function (response) {
                eventBus.publish('categoria_guardada', response.data);
                $scope.categoria = {};

            })
            .catch(function (err) {
                eventBus.publish('error_guardado', err);
            });
    };

    // Buscar categorías
    $scope.buscar = function (nombre) {
        if (!nombre || nombre.trim() === '') {
            categoriaService.cargarTodas();
            $scope.mostrarTodos = true;
            return;
        }

        categoriaService.buscar(nombre);
        $scope.mostrarTodos = false;
    };

    // Limpiar búsqueda
    $scope.limpiarBusqueda = function () {
        $scope.nombre = '';
        categoriaService.cargarTodas();
        $scope.mostrarTodos = true;
    };

    // Verificar estado de Pusher
    $scope.verificarPusher = function () {
       
        categoriaService.cargarTodas(); // Recargar manualmente
    };
});

app.controller("clientesCtrl", function ($scope, $http) {
    $scope.clientes = []
    $scope.searching = false;
    $scope.allData = function () {
        $http.get("/clientes/all").then(function (res) {
            $("#tablaClientes").html(res.data)
        })
    }

    //inizializa el template
    $scope.$on('$viewContentLoaded', function () {
        $scope.allData()
    });

    Pusher.logToConsole = true
    var pusher = new Pusher("db840e3e13b1c007269e", {
        cluster: 'us2'
    })
    var channel = pusher.subscribe("canalClientes");
    channel.bind("newDataInserted", function (data) {
        if (!$scope.searching)
            $scope.allData();
    })

    $scope.buscar = function (nombre) {
        if (!nombre || nombre.trim() === '') {
            $scope.searching = false
            $scope.allData(); // Si la búsqueda está vacía, mostrar todos
            return;
        }

        $http.get("/clientes/buscar", {
            params: {
                busqueda: nombre
            }
        }).then(function (response) {
        

            $("#tablaClientes").html(response.data);
            $scope.searching = true;
        }, function (error) {
            console.error("Error en búsqueda:", error);
        })
    }
    // Guardar cliente
    $scope.guardar = function (cliente) {
        $http.post("/clientes/agregar", cliente).then(function () {
            $scope.cliente = {}
        }, function (err) {
            console.log("Error al guardar: " + (err.data ? err.message : ""))
        })
    }
})

app.controller("lugaresCtrl", function ($scope, $http) {
    $scope.lugares = []
    $scope.searching = false;

    $scope.allData = function () {
        $http.get("/lugares/all").then(function (res) {
            $("#tablaLugares").html(res.data)
        })
    }
    //inizializa el template
    $scope.$on('$viewContentLoaded', function () {
        $scope.allData()
    });

    Pusher.logToConsole = true
    var pusher = new Pusher("db840e3e13b1c007269e", {
        cluster: 'us2'
    })
    var channel = pusher.subscribe("canalLugares");
    channel.bind("newDataInserted", function (data) {
        if (!$scope.searching)
            $scope.allData();
    })
    // Guardar lugar
    $scope.guardar = function (lugar) {
        $http.post("/lugar/guardar", lugar).then(function () {
            $scope.lugar = {}
            $scope.allData()
        }, function (err) {
            console.log("Error al guardar: " + (err.data ? err.message : ""))
        })
    }

    $scope.buscar = function (lugar) {
        if (!lugar || lugar.trim() === '') {
            $scope.searching = false
            $scope.allData();
            return;

        }

        $http.get("/lugar/buscar", {
            params: {
                busqueda: lugar
            }
        }).then(function (response) {
        

            $("#tablaLugares").html(response.data);
            $scope.searching = true;
        }, function (error) {
            console.error("Error en búsqueda:", error);
        })
    }
})

const DateTime = luxon.DateTime
let lxFechaHora

document.addEventListener("DOMContentLoaded", function (event) {
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