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
    $scope.categorias = []

    // Obtener lista de categorías
    $http.get("/categorias").then(function (res) {
        $scope.categorias = res.data
    })

    // Guardar categoría
    $scope.guardar = function (categoria) {
        $http.post("/categorias/agregar", categoria).then(function () {
            alert("Categoría guardada")
            // Recargar lista sin recargar toda la página
            $http.get("/categorias").then(function (res) {
                $scope.categorias = res.data
            })
            $scope.categoria = {} // Limpiar formulario
        }, function (err) {
            alert("Error al guardar: " + (err.data?.message || ""))
        })
    }

    // Eliminar categoría
    $scope.eliminar = function (idCategoria) {
        $http.post("/categoria/eliminar", { idCategoria: idCategoria }).then(function () {
            alert("Categoría eliminada")
            $http.get("/categorias").then(function (res) {
                $scope.categorias = res.data
            })
        }, function (err) {
            alert("Error al eliminar: " + (err.data?.message || ""))
        })
    }
})

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


