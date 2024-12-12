# Maintainer: Your Name <your.email@example.com>
# Contributor: Your Name <your.email@example.com>

pkgname=pk
pkgver=1.0.0
pkgrel=1
pkgdesc="A lightweight package manager for Arch Linux"
arch=('any')
url="https://github.com/yourusername/pk"  # Update this with your actual GitHub URL
license=('MIT')
depends=('python' 'python-requests' 'python-colorama' 'python-tqdm')  # Added python-tqdm as dependency
makedepends=('git' 'python-setuptools')  # Dependencies for building the package
source=("pk.py"
        "requirements.txt"
        "aur.py"  # Add aur.py to the source array
        "repo.py"
        "dependencies.py")  # Added dependencies.py
sha256sums=('SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP')  # SKIP checksum as needed, or provide actual checksums

# Optionally, clean up previous build if the directory exists
prepare() {
  # Clean up any previously generated package files or directories to avoid conflicts
  if [ -d "$srcdir/$pkgname-$pkgver" ]; then
    echo "Removing old build directory..."
    rm -rf "$srcdir/$pkgname-$pkgver"
  fi
}

package() {
  cd "$srcdir"

  # Install the main script globally
  install -Dm755 pk.py "$pkgdir/usr/bin/pk"

  # Install the requirements.txt file
  install -Dm644 requirements.txt "$pkgdir/usr/share/pk/requirements.txt"

  # Install the aur.py and repo.py modules
  install -Dm644 aur.py "$pkgdir/usr/share/pk/aur.py"
  install -Dm644 repo.py "$pkgdir/usr/share/pk/repo.py"
  install -Dm644 dependencies.py "$pkgdir/usr/share/pk/dependencies.py"

  # Optionally, install other files (man pages, docs, etc.)
  # install -Dm644 your_man_page.1 "$pkgdir/usr/share/man/man1/pk.1"
}
