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
app.run(["$rootScope", "$location", "$timeout", function ($rootScope, $location, $timeout) {
    function actualizarFechaHora() {
        lxFechaHora = DateTime
            .now()
            .setLocale("es")

        $rootScope.angularjsHora = lxFechaHora.toFormat("hh:mm:ss a")
        $timeout(actualizarFechaHora, 1000)
    }

    $rootScope.slide = ""

    actualizarFechaHora()

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

app.controller("appCtrl", function ($scope, $http) { })


app.controller("eventosCtrl", function ($scope, $http) {

    $scope.eventos = []

    // Obtener lista de eventos
    $http.get("/eventos").then(function (res) {
        $scope.eventos = res.data
    })

})

app.controller("categoriasCtrl", function ($scope, $http) {
    $scope.categorias = [];
    $scope.terminoBusqueda = '';
    $scope.categoria = {}; // Objeto para el formulario

    // Función para cargar categorías
    $scope.cargarCategorias = function () {
        if ($scope.terminoBusqueda) {
            $http.get("/categorias/buscar", {
                params: { busqueda: $scope.terminoBusqueda }
            }).then(function (response) {
                $scope.categorias = response.data;
            }, function (error) {
                console.error("Error en búsqueda:", error);
                alert("Error al buscar categorías");
            });
        } else {
            $http.get("/categorias/json").then(function (response) {
                $scope.categorias = response.data;
            }, function (error) {
                console.error("Error al cargar categorías:", error);
                alert("Error al cargar categorías");
            });
        }
    };

    // Cargar categorías al inicializar
    $scope.cargarCategorias();

    // Guardar categoría
    $scope.guardar = function (categoria) {
        $http.post("/categorias/agregar", categoria).then(function (response) {
            alert("Categoría guardada");

            // Disparar evento Pusher después de guardar
            $http.get("/pusherCategorias").then(function () {
                console.log("Evento Pusher disparado");
            });

            $scope.categoria = {}; // Limpiar formulario
        }, function (err) {
            alert("Error al guardar: " + (err.data ? err.message : ""));
        });
    };

    // Función de búsqueda
    $scope.buscar = function () {
        $scope.cargarCategorias();
    };

    // Limpiar búsqueda
    $scope.limpiarBusqueda = function () {
        $scope.terminoBusqueda = '';
        $scope.cargarCategorias();
    };

    // Configuración de Pusher
    Pusher.logToConsole = true;

    var pusher = new Pusher("db840e3e13b1c007269e", {
        cluster: 'us2'
    });

    var channel = pusher.subscribe("canalCategorias");
    channel.bind("eventoCategorias", function (data) {
        // Actualizar la tabla cuando llegue evento de Pusher
        $scope.$apply(function () {
            $scope.cargarCategorias();
        });
        console.log("Tabla actualizada por Pusher", data);
    });
});


app.controller("clientesCtrl", function ($scope, $http) {
    $scope.clientes = []

    //inizializa el template
    $http.get("/clientes").then(function (res) { console.log("resultado", res.data) })

    $scope.allData = function () {
        $http.get("/clientes/buscar").then(function (res) {
            console.log("resultado", res.data)
            $("#tablaClientes").html(res)
        })
    }
    // Guardar cliente
    $scope.guardar = function (cliente) {
        $http.post("/clientes/agregar", cliente).then(function () {
            console.log("cliente guardada")
            // Recargar lista sin recargar toda la página
            $scope.allData()
            $scope.cliente = {} // Limpiar formulario
        }, function (err) {
            console.log("Error al guardar: " + (err.data ? err.message : ""))
        })
    }
})


app.controller("lugaresCtrl", function ($scope, $http) {
    $scope.lugares = []

    // Obtener lista de lugares - corregí para usar $http
    $http.get("/lugares").then(function (res) {
        $scope.lugares = res.data
    })

    // Guardar lugar
    $scope.guardar = function (lugar) {
        $http.post("/lugar", lugar).then(function () {
            alert("Lugar guardado")
            location.reload()
        })
    }
})

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