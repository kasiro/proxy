{
  description = "Моя среда разработки";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      # Определяем систему, на которой вы работаете
      system = "x86_64-linux"; # или aarch64-linux, x86_64-darwin
      pkgs = import nixpkgs { inherit system; };
    in
    {
      # Определяем devShell
      devShells.${system}.default = pkgs.mkShell {
        # Пакеты, которые будут доступны в вашей среде
        packages = with pkgs; [
          python3
        ];

        # Переменные окружения (опционально)
        # MY_VAR = "some-value";

        # Команды, выполняемые при входе в оболочку (опционально)
        shellHook = ''
          echo "Добро пожаловать в среду разработки!";
          ./setup.sh
        '';
      };
    };
}
