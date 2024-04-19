const numeros =  [5, 10, 15, 20, 25]

var soma = numeros.reduce(function(soma, numero){
    return numero + soma;
})

console.log(soma)