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

    $rootScope.$on("$routeChangeSuccess", function (event, current, previous) {
        $("html").css("overflow-x", "hidden")

        const path = current.$$route.originalPath

        if (path.indexOf("splash") == -1) {
            const active = $(".app-menu .nav-link.active").parent().index()
            const click  = $(`[href^="#${path}"]`).parent().index()

            if (active != click) {
                $rootScope.slide  = "animate__animated animate__faster animate__slideIn"
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

app.controller("appCtrl", function ($scope, $http) {
})

// Eliminé el controlador productosCtrl ya que no tienes ruta para él
app.controller("eventosCtrl", function ($scope, $http) {
})

app.controller("categoriasCtrl", function ($scope, $http) {
  $scope.categorias = [];
    $scope.nuevaCategoria = {};
    
    $scope.init = function() {
        $scope.cargarCategorias();
    };

    // Cargar categorías desde API
    $scope.cargarCategorias = function() {
        $http.get("/api/categorias")
        .then(function(response) {
            $scope.categorias = response.data;
        })
        .catch(function(error) {
            console.error("Error al cargar categorías:", error);
            alert("Error al cargar las categorías");
        });
    };

    // Guardar categoría
    $scope.guardar = function() {
        $http.post("/api/categorias/agregar", $scope.nuevaCategoria)
        .then(function(response) {
            alert(response.data.message);
            $scope.nuevaCategoria = {}; // Limpiar formulario
            $scope.cargarCategorias(); // Recargar lista
        })
        .catch(function(error) {
            console.error("Error:", error);
            alert("Error al guardar la categoría");
        });
    };

    // Eliminar categoría
    $scope.eliminar = function(id) {
        if (confirm('¿Estás seguro de que quieres eliminar esta categoría?')) {
            $http.post("/api/categoria/eliminar", {idCategoria: id})
            .then(function(response) {
                alert(response.data.message);
                $scope.cargarCategorias(); // Recargar lista
            })
            .catch(function(error) {
                console.error("Error:", error);
                alert("Error al eliminar la categoría");
            });
        }
    };
});

app.controller("clientesCtrl", function ($scope, $http) {
    $scope.clientes = []

    // Obtener lista de clientes - corregí para usar $http
    $http.get("/clientes").then(function (res) {
        $scope.clientes = res.data
    })

    // Guardar cliente
    $scope.guardar = function (cliente) {
        $http.post("/cliente", cliente).then(function () {
            alert("Cliente guardado")
            location.reload()
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





